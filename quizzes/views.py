from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    AttemptQuestion,
    AttemptQuestionOption,
    Category,
    Quiz,
    QuizAttempt,
)


def quiz_list(request):
    quizzes = Quiz.objects.filter(status=Quiz.Status.PUBLISHED).select_related(
        "category", "author"
    )
    categories = Category.objects.all()

    current_category = None
    slug = request.GET.get("category")
    if slug:
        current_category = get_object_or_404(Category, slug=slug)
        quizzes = quizzes.filter(category=current_category)

    return render(
        request,
        "quizzes/quiz_list.html",
        {
            "quizzes": quizzes,
            "categories": categories,
            "current_category": current_category,
        },
    )


def quiz_detail(request, slug):
    quiz = get_object_or_404(
        Quiz.objects.select_related("category", "author"),
        slug=slug,
        status=Quiz.Status.PUBLISHED,
    )

    attempts = []
    in_progress = None
    if request.user.is_authenticated:
        attempts = quiz.attempts.filter(user=request.user).order_by("-started_at")
        in_progress = attempts.filter(status=QuizAttempt.Status.IN_PROGRESS).first()

    return render(
        request,
        "quizzes/quiz_detail.html",
        {
            "quiz": quiz,
            "questions_count": quiz.questions.count(),
            "attempts": attempts,
            "in_progress": in_progress,
        },
    )


@login_required
@require_POST
def quiz_start(request, slug):
    quiz = get_object_or_404(Quiz, slug=slug, status=Quiz.Status.PUBLISHED)

    if not quiz.questions.exists():
        messages.error(request, "У цьому тесті ще немає питань.")
        return redirect("quiz_detail", slug=quiz.slug)

    attempt = quiz.attempts.filter(
        user=request.user, status=QuizAttempt.Status.IN_PROGRESS
    ).first()
    if attempt is None or _is_expired(attempt):
        if attempt is not None:
            attempt.status = QuizAttempt.Status.ABANDONED
            attempt.save(update_fields=["status", "updated_at"])
        attempt = QuizAttempt.objects.create(
            quiz=quiz, user=request.user, started_at=timezone.now()
        )

    return redirect("attempt_take", pk=attempt.pk)


def _deadline(attempt):
    """time_limit вважається хвилинами."""
    if not attempt.quiz.time_limit:
        return None
    return attempt.started_at + timedelta(minutes=attempt.quiz.time_limit)


def _is_expired(attempt):
    deadline = _deadline(attempt)
    return deadline is not None and timezone.now() > deadline


@login_required
def attempt_take(request, pk):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz"), pk=pk, user=request.user
    )

    if attempt.status != QuizAttempt.Status.IN_PROGRESS:
        if attempt.status == QuizAttempt.Status.COMPLETED:
            return redirect("attempt_result", pk=attempt.pk)
        messages.error(request, "Цю спробу завершено без результату.")
        return redirect("quiz_detail", slug=attempt.quiz.slug)

    if _is_expired(attempt):
        attempt.status = QuizAttempt.Status.ABANDONED
        attempt.save(update_fields=["status", "updated_at"])
        messages.error(request, "Час вичерпано, спробу не зараховано.")
        return redirect("quiz_detail", slug=attempt.quiz.slug)

    questions = list(
        attempt.quiz.questions.prefetch_related("answers").order_by("sort_order", "id")
    )

    if request.method == "POST":
        _grade_attempt(attempt, questions, request.POST)
        return redirect("attempt_result", pk=attempt.pk)

    return render(
        request,
        "quizzes/attempt_take.html",
        {
            "attempt": attempt,
            "quiz": attempt.quiz,
            "questions": questions,
            "deadline": _deadline(attempt),
        },
    )


@transaction.atomic
def _grade_attempt(attempt, questions, post_data):
    total_points = 0
    earned_points = 0
    correct_count = 0

    for question in questions:
        answers = sorted(question.answers.all(), key=lambda a: (a.sort_order, a.id))
        valid_ids = {a.id for a in answers}
        correct_ids = {a.id for a in answers if a.is_correct}

        raw = post_data.getlist(f"question_{question.id}")
        selected_ids = {int(v) for v in raw if v.isdigit()} & valid_ids
        if question.type == question.QuestionType.SINGLE:
            selected_ids = set(list(selected_ids)[:1])

        is_correct = bool(correct_ids) and selected_ids == correct_ids
        earned = question.points if is_correct else 0

        attempt_question = AttemptQuestion.objects.create(
            attempt=attempt,
            question=question,
            is_correct=is_correct,
            earned_points=earned,
        )
        AttemptQuestionOption.objects.bulk_create(
            [
                AttemptQuestionOption(attempt_question=attempt_question, answer_id=i)
                for i in selected_ids
            ]
        )

        total_points += question.points
        earned_points += earned
        correct_count += int(is_correct)

    attempt.total_questions = len(questions)
    attempt.correct_answers = correct_count
    attempt.wrong_answers = len(questions) - correct_count
    attempt.total_points = total_points
    attempt.earned_points = earned_points
    attempt.score = (
        (Decimal(earned_points) / Decimal(total_points) * 100).quantize(Decimal("0.01"))
        if total_points
        else Decimal("0.00")
    )
    attempt.status = QuizAttempt.Status.COMPLETED
    attempt.completed_at = timezone.now()
    attempt.save()


@login_required
def attempt_result(request, pk):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz"),
        pk=pk,
        user=request.user,
        status=QuizAttempt.Status.COMPLETED,
    )

    attempt_questions = (
        attempt.questions.select_related("question")
        .prefetch_related("selected_options", "question__answers")
        .order_by("question__sort_order", "question_id")
    )

    review = []
    for aq in attempt_questions:
        selected_ids = {o.answer_id for o in aq.selected_options.all()}
        answers = sorted(
            aq.question.answers.all(), key=lambda a: (a.sort_order, a.id)
        )
        review.append(
            {
                "aq": aq,
                "answers": [
                    {"answer": a, "selected": a.id in selected_ids} for a in answers
                ],
            }
        )

    return render(
        request,
        "quizzes/attempt_result.html",
        {"attempt": attempt, "review": review},
    )


@login_required
def my_attempts(request):
    attempts = QuizAttempt.objects.filter(user=request.user).select_related("quiz")
    return render(request, "quizzes/my_attempts.html", {"attempts": attempts.order_by("-started_at")})


def register(request):
    if request.user.is_authenticated:
        return redirect("quiz_list")

    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("quiz_list")

    return render(request, "registration/register.html", {"form": form})
