# Створюємо Django Quiz з нуля: покроковий курс

Цей посібник дає змогу відтворити застосунок у чистій теці, навіть якщо немає жодного файлу з репозиторію. Наведено планування, налаштування середовища, встановлення Django, повні лістинги потрібних Python та HTML файлів, запуск і перевірку.

## 1. Що створимо і як плануватимемо роботу

Застосунок дозволяє переглядати опубліковані тести за категоріями, зареєструватися й увійти, пройти тест з одиночними та множинними питаннями, отримати оцінку та переглянути історію. Автор готує категорії, тести, питання й відповіді через Django Admin.

Працюватимемо поетапно: запустимо порожній проєкт; під’єднаємо застосунок; опишемо модель даних; створимо таблиці; налаштуємо адмінку; побудуємо URL і сторінки; пройдемо сценарій користувача. Це дозволяє перевіряти кожен шар окремо.

## 2. Поняття Django, які використовуємо

- **Проєкт Django** — загальна конфігурація сайту. Тут це пакет `config` із налаштуваннями та кореневими URL.
- **Застосунок (app)** — частина проєкту з окремою відповідальністю. `quizzes` містить моделі, сторінки й адмінку.
- **Віртуальне середовище** — окрема директорія Python-залежностей для ізоляції пакетів.
- **Модель** — Python-клас, що описує таблицю бази даних. Поля класу стають стовпцями.
- **Міграція** — інструкція Django створити або змінити таблиці. `makemigrations` генерує її з моделей, `migrate` застосовує.
- **URL-маршрут** — правило, яке зіставляє адресу запиту з обробником.
- **View (подання)** — Python-функція, яка обробляє запит і повертає відповідь.
- **Template (шаблон)** — HTML з Django Template Language: `{{ ... }}` виводить значення, `{% ... %}` виконує цикл, умову чи іншу команду.
- **ORM** — інтерфейс до бази через Python (`Quiz.objects.filter(...)`) замість ручного SQL.
- **Django Admin** — готовий інтерфейс керування даними на основі моделей.
- **Автентифікація** визначає, хто увійшов; `login_required` закриває сторінку для гостей. **CSRF-токен** захищає POST-форми від підроблених запитів.

## 3. Python, тека проєкту та віртуальне середовище

Потрібен Python 3.12 або сумісніший випуск. Перевірте його:

```bash
python3 --version
```

У Windows використовуйте `py -3 --version` та замініть `python3` у командах на `py -3`. Створіть теку проєкту та середовище:

```bash
mkdir django-quiz
cd django-quiz
python3 -m venv .venv
```

Активуйте середовище:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell (замість попередньої команди)
.venv\Scripts\Activate.ps1
```

Встановіть Django й збережіть список пакетів:

```bash
python -m pip install --upgrade pip
python -m pip install Django
python -m pip freeze > requirements.txt
python -m django --version
```

`pip` — менеджер пакетів Python. Файл `requirements.txt` дозволяє повторити встановлення через `python -m pip install -r requirements.txt`. SQLite включена у Python і вже налаштована Django, окремий сервер бази на початку не потрібен.

## 4. Згенеруйте основу та створіть каталоги шаблонів

Команди виконуйте з кореня `django-quiz`:

```bash
django-admin startproject config .
python manage.py startapp quizzes
mkdir -p quizzes/templates/quizzes quizzes/templates/registration
```

Крапка після `config` означає створити проєкт у поточній теці. У Windows каталоги можна створити файловим менеджером. Django створить `__init__.py`; ці файли пакетів залиште порожніми. Файли нижче створіть або повністю замініть їхній вміст наведеними лістингами.

## 5. Структура даних

```text
Category 1 ── * Quiz 1 ── * Question 1 ── * Answer
                     │
                     └── * QuizAttempt 1 ── * AttemptQuestion 1 ── * AttemptQuestionOption
```

`Category` — категорія, `Quiz` — тест та автор, `Question` — питання, `Answer` — варіант. `QuizAttempt` зберігає користувача, стан і підсумкові бали. `AttemptQuestion` фіксує результат на питання, а `AttemptQuestionOption` — вибрані відповіді.

`CharField` зберігає короткий текст, `TextField` — довгий, `SlugField` — рядок для URL, `BooleanField` — так/ні, `PositiveIntegerField` — невід’ємне число. `null=True` дозволяє NULL у базі; `blank=True` дозволяє порожнє поле у формах. `auto_now_add` записує дату створення, `auto_now` оновлює її при збереженні. `related_name` створює зворотний доступ, наприклад `category.quizzes.all()`.

`ForeignKey` задає зв’язок «багато до одного». `CASCADE` видаляє дочірні записи, `PROTECT` забороняє видалити запис, поки на нього посилаються. `TextChoices` задає обмежені стани, `UniqueConstraint` — унікальність комбінації полів.

## 6. Повні лістинги файлів

Шлях у заголовку вказано від кореня проєкту. Переносьте кожен лістинг повністю.

### `manage.py`

CLI команди проєкту: запуск сервера, міграції, перевірки та створення адміністратора.

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

```

### `config/settings.py`

Головні параметри. INSTALLED_APPS під’єднує компоненти; MIDDLEWARE обробляє запит; TEMPLATES налаштовує HTML; DATABASES задає SQLite; LOGIN_* визначають перенаправлення.

```python
"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 6.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-kjx$laj_$p&8i!yx#6!#(qkn23#7*r6)i5h9xvx1@%j*x4o**&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'quizzes.apps.QuizzesConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'quiz_list'
LOGOUT_REDIRECT_URL = 'quiz_list'

```

### `config/urls.py`

Кореневі маршрути: admin, стандартні auth URL-и Django та маршрути app quizzes.

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("quizzes.urls")),
]

```

### `config/wsgi.py`

Точка входу WSGI для синхронних серверів розгортання.

```python
"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

```

### `config/asgi.py`

Точка входу ASGI для асинхронних серверів.

```python
"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()

```

### `quizzes/apps.py`

Метадані застосунку, на які посилається INSTALLED_APPS.

```python
from django.apps import AppConfig


class QuizzesConfig(AppConfig):
    name = 'quizzes'

```

### `quizzes/models.py`

Схема бази. ForeignKey створює зв’язок; related_name дає зворотний доступ; TextChoices задає стани; UniqueConstraint забороняє дублікати.

```python
from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Quiz(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="quizzes")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="quizzes")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    time_limit = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    class QuestionType(models.TextChoices):
        SINGLE = "single", "Single"
        MULTIPLE = "multiple", "Multiple"

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    type = models.CharField(max_length=20, choices=QuestionType.choices, default=QuestionType.SINGLE, db_index=True)
    points = models.PositiveIntegerField(default=1)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.TextField()
    is_correct = models.BooleanField(default=False, db_index=True)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        ABANDONED = "abandoned", "Abandoned"

    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT, related_name="attempts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="quiz_attempts")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS, db_index=True)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    total_points = models.PositiveIntegerField(default=0)
    earned_points = models.PositiveIntegerField(default=0)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.quiz}"


class AttemptQuestion(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="questions")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="attempt_questions")
    is_correct = models.BooleanField(default=False, db_index=True)
    earned_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"],
                name="unique_attempt_question",
            )
        ]

    def __str__(self):
        return f"{self.attempt} - {self.question}"


class AttemptQuestionOption(models.Model):
    attempt_question = models.ForeignKey(AttemptQuestion, on_delete=models.CASCADE, related_name="selected_options")
    answer = models.ForeignKey(Answer, on_delete=models.PROTECT, related_name="selected_in_attempts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt_question", "answer"],
                name="unique_attempt_question_option",
            )
        ]

    def __str__(self):
        return f"{self.attempt_question} - {self.answer}"
```

### `quizzes/admin.py`

Реєстрація моделей в адмінці; ModelAdmin налаштовує списки, а TabularInline редагує дочірні записи разом із батьківським.

```python
from django.contrib import admin

from .models import (
    Answer,
    AttemptQuestion,
    AttemptQuestionOption,
    Category,
    Question,
    Quiz,
    QuizAttempt,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "status", "time_limit")
    list_filter = ("status", "category")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [QuestionInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "type", "points", "sort_order")
    list_filter = ("quiz", "type")
    inlines = [AnswerInline]


class AttemptQuestionInline(admin.TabularInline):
    model = AttemptQuestion
    extra = 0


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "status", "started_at", "completed_at")
    list_filter = ("status", "quiz")
    inlines = [AttemptQuestionInline]


admin.site.register(AttemptQuestionOption)

```

### `quizzes/urls.py`

Маршрути app. Конвертери slug та int перевіряють частини URL; name використовується у шаблонах і redirect().

```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.quiz_list, name="quiz_list"),
    path("register/", views.register, name="register"),
    path("my-attempts/", views.my_attempts, name="my_attempts"),
    path("quiz/<slug:slug>/", views.quiz_detail, name="quiz_detail"),
    path("quiz/<slug:slug>/start/", views.quiz_start, name="quiz_start"),
    path("attempt/<int:pk>/", views.attempt_take, name="attempt_take"),
    path("attempt/<int:pk>/result/", views.attempt_result, name="attempt_result"),
]

```

### `quizzes/views.py`

Обробники запитів. ORM шукає дані, render формує HTML, redirect перенаправляє, get_object_or_404 повертає 404. Декоратори обмежують доступ/метод запиту; atomic зберігає оцінювання транзакційно.

```python
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

```

### `quizzes/tests.py`

Автоматичні тести основних сценаріїв. `TestCase` створює ізольовану тестову базу для кожного тестового запуску; `setUp()` готує користувачів і тестові дані перед кожним методом `test_...`.

```python
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Answer, Category, Question, Quiz, QuizAttempt

User = get_user_model()


class QuizFlowTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user("author", password="x")
        self.user = User.objects.create_user("student", password="x")
        self.other = User.objects.create_user("other", password="x")
        cat = Category.objects.create(name="Python", slug="python")
        self.quiz = Quiz.objects.create(
            category=cat, author=self.author, title="Basics", slug="basics",
            status=Quiz.Status.PUBLISHED, time_limit=10,
        )
        self.draft = Quiz.objects.create(
            category=cat, author=self.author, title="Draft", slug="draft",
        )
        self.q1 = Question.objects.create(quiz=self.quiz, text="2+2?", points=2)
        self.a1 = Answer.objects.create(question=self.q1, text="4", is_correct=True)
        self.a2 = Answer.objects.create(question=self.q1, text="5")
        self.q2 = Question.objects.create(
            quiz=self.quiz, text="Even?", type=Question.QuestionType.MULTIPLE, points=3
        )
        self.b1 = Answer.objects.create(question=self.q2, text="2", is_correct=True)
        self.b2 = Answer.objects.create(question=self.q2, text="4", is_correct=True)
        self.b3 = Answer.objects.create(question=self.q2, text="3")

    def start(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse("quiz_start", args=["basics"]))
        attempt = QuizAttempt.objects.get(user=self.user)
        self.assertRedirects(r, reverse("attempt_take", args=[attempt.pk]))
        return attempt

    def test_pages_render(self):
        self.assertContains(self.client.get(reverse("quiz_list")), "Basics")
        self.assertNotContains(self.client.get(reverse("quiz_list")), "Draft")
        self.assertEqual(self.client.get(reverse("quiz_detail", args=["draft"])).status_code, 404)
        self.assertEqual(self.client.get(reverse("quiz_detail", args=["basics"])).status_code, 200)

    def test_start_requires_login(self):
        r = self.client.post(reverse("quiz_start", args=["basics"]))
        self.assertEqual(r.status_code, 302)
        self.assertIn("login", r.url)

    def test_full_pass(self):
        attempt = self.start()
        self.assertContains(self.client.get(reverse("attempt_take", args=[attempt.pk])), "2+2?")
        r = self.client.post(reverse("attempt_take", args=[attempt.pk]), {
            f"question_{self.q1.id}": [self.a1.id],
            f"question_{self.q2.id}": [self.b1.id, self.b2.id],
        })
        self.assertRedirects(r, reverse("attempt_result", args=[attempt.pk]))
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, "completed")
        self.assertEqual((attempt.correct_answers, attempt.wrong_answers), (2, 0))
        self.assertEqual((attempt.earned_points, attempt.total_points), (5, 5))
        self.assertEqual(float(attempt.score), 100.0)
        self.assertContains(self.client.get(reverse("attempt_result", args=[attempt.pk])), "100")

    def test_partial_multiple_is_wrong(self):
        attempt = self.start()
        self.client.post(reverse("attempt_take", args=[attempt.pk]), {
            f"question_{self.q1.id}": [self.a1.id],
            f"question_{self.q2.id}": [self.b1.id],
        })
        attempt.refresh_from_db()
        self.assertEqual((attempt.correct_answers, attempt.earned_points), (1, 2))
        self.assertEqual(float(attempt.score), 40.0)

    def test_foreign_answer_ignored_and_blank_ok(self):
        attempt = self.start()
        self.client.post(reverse("attempt_take", args=[attempt.pk]), {
            f"question_{self.q1.id}": [self.b1.id],
        })
        attempt.refresh_from_db()
        self.assertEqual(attempt.correct_answers, 0)
        self.assertEqual(attempt.status, "completed")

    def test_other_user_cannot_see_attempt(self):
        attempt = self.start()
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("attempt_take", args=[attempt.pk])).status_code, 404)

    def test_expired_attempt_abandoned(self):
        attempt = self.start()
        QuizAttempt.objects.filter(pk=attempt.pk).update(
            started_at=timezone.now() - timedelta(minutes=11)
        )
        self.client.get(reverse("attempt_take", args=[attempt.pk]))
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, "abandoned")

    def test_register_and_my_attempts(self):
        r = self.client.post(reverse("register"), {
            "username": "newbie", "password1": "S3cretPass!xyz", "password2": "S3cretPass!xyz",
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.client.get(reverse("my_attempts")).status_code, 200)

```

### `quizzes/templates/base.html`

Базова HTML-структура. Дочірні сторінки заповнюють блоки; csrf_token захищає POST-форми.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Quizzes{% endblock %}</title>
</head>
<body>
    <header>
        <nav>
            <a href="{% url 'quiz_list' %}">Quizzes</a>
            {% if user.is_authenticated %}
                | <a href="{% url 'my_attempts' %}">My Attempts</a>
                {% if user.is_staff %}| <a href="{% url 'admin:index' %}">Admin</a>{% endif %}
                | {{ user.get_username }}
                <form method="post" action="{% url 'logout' %}" style="display:inline">
                    {% csrf_token %}
                    <button type="submit">Log out</button>
                </form>
            {% else %}
                | <a href="{% url 'login' %}">Log in</a>
                | <a href="{% url 'register' %}">Register</a>
            {% endif %}
        </nav>
        <hr>
    </header>

    {% if messages %}
        <ul>
            {% for message in messages %}
                <li>{{ message }}</li>
            {% endfor %}
        </ul>
    {% endif %}

    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### `quizzes/templates/registration/login.html`

Шаблон стандартної форми входу Django.

```html
{% extends "base.html" %}

{% block title %}Login{% endblock %}

{% block content %}
<h1>Login</h1>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="hidden" name="next" value="{{ next }}">
    <button type="submit">Log in</button>
</form>

<p><a href="{% url 'register' %}">Register</a></p>
{% endblock %}
```

### `quizzes/templates/registration/register.html`

Форма реєстрації на основі UserCreationForm.

```html
{% extends "base.html" %}

{% block title %}Registration{% endblock %}

{% block content %}
<h1>Registration</h1>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Register</button>
</form>

<p><a href="{% url 'login' %}">Already have an account?</a></p>
{% endblock %}
```

### `quizzes/templates/quizzes/quiz_list.html`

Каталог і фільтр за категоріями. Цикл for показує кожен тест.

```html
{% extends "base.html" %}

{% block title %}Quizzes{% endblock %}

{% block content %}
<h1>Quizzes{% if current_category %}: {{ current_category.name }}{% endif %}</h1>

<h2>Categories</h2>
<ul>
    <li><a href="{% url 'quiz_list' %}">All</a></li>
    {% for category in categories %}
        <li><a href="{% url 'quiz_list' %}?category={{ category.slug }}">{{ category.name }}</a></li>
    {% endfor %}
</ul>

<h2>List</h2>
{% if quizzes %}
    <ul>
        {% for quiz in quizzes %}
            <li>
                <a href="{% url 'quiz_detail' quiz.slug %}">{{ quiz.title }}</a>
                ({{ quiz.category.name }}, author: {{ quiz.author }})
                {% if quiz.time_limit %}, limit: {{ quiz.time_limit }} min{% endif %}
            </li>
        {% endfor %}
    </ul>
{% else %}
    <p>No quizzes available yet.</p>
{% endif %}
{% endblock %}
```

### `quizzes/templates/quizzes/quiz_detail.html`

Опис тесту, спроби користувача та форма старту/продовження.

```html
{% extends "base.html" %}

{% block title %}{{ quiz.title }}{% endblock %}

{% block content %}
<h1>{{ quiz.title }}</h1>

<p>Category: <a href="{% url 'quiz_list' %}?category={{ quiz.category.slug }}">{{ quiz.category.name }}</a></p>
<p>Author: {{ quiz.author }}</p>
<p>Questions: {{ questions_count }}</p>
<p>Time limit: {% if quiz.time_limit %}{{ quiz.time_limit }} min{% else %}none{% endif %}</p>

{% if quiz.description %}
    <p>{{ quiz.description|linebreaksbr }}</p>
{% endif %}

{% if user.is_authenticated %}
    {% if in_progress %}
        <p><a href="{% url 'attempt_take' in_progress.pk %}">Continue attempt</a></p>
    {% endif %}
    <form method="post" action="{% url 'quiz_start' quiz.slug %}">
        {% csrf_token %}
        <button type="submit">{% if in_progress %}Continue{% else %}Start{% endif %}</button>
    </form>

    <h2>My Attempts</h2>
    {% if attempts %}
        <table border="1" cellpadding="4">
            <tr>
                <th>Date</th>
                <th>Status</th>
                <th>Result</th>
                <th></th>
            </tr>
            {% for attempt in attempts %}
                <tr>
                    <td>{{ attempt.started_at }}</td>
                    <td>{{ attempt.get_status_display }}</td>
                    <td>{% if attempt.status == "completed" %}{{ attempt.score }}%{% else %}—{% endif %}</td>
                    <td>
                        {% if attempt.status == "completed" %}
                            <a href="{% url 'attempt_result' attempt.pk %}">View</a>
                        {% elif attempt.status == "in_progress" %}
                            <a href="{% url 'attempt_take' attempt.pk %}">Continue</a>
                        {% endif %}
                    </td>
                </tr>
            {% endfor %}
        </table>
    {% else %}
        <p>No attempts yet.</p>
    {% endif %}
{% else %}
    <p><a href="{% url 'login' %}?next={{ request.path }}">Log in</a> to take the quiz.</p>
{% endif %}
{% endblock %}
```

### `quizzes/templates/quizzes/attempt_take.html`

Форма відповідей: radio для одного варіанта, checkbox для множинних.

```html
{% extends "base.html" %}

{% block title %}{{ quiz.title }}{% endblock %}

{% block content %}
<h1>{{ quiz.title }}</h1>

{% if deadline %}
    <p>Complete by: {{ deadline }}</p>
{% endif %}

<form method="post">
    {% csrf_token %}

    {% for question in questions %}
        <fieldset>
            <legend>
                {{ forloop.counter }}. {{ question.text }}
                ({{ question.points }} pts,
                {% if question.type == "multiple" %}multiple answers{% else %}single answer{% endif %})
            </legend>

            {% for answer in question.answers.all %}
                <div>
                    <label>
                        {% if question.type == "multiple" %}
                            <input type="checkbox" name="question_{{ question.id }}" value="{{ answer.id }}">
                        {% else %}
                            <input type="radio" name="question_{{ question.id }}" value="{{ answer.id }}">
                        {% endif %}
                        {{ answer.text }}
                    </label>
                </div>
            {% endfor %}
        </fieldset>
        <br>
    {% endfor %}

    <button type="submit">Finish</button>
</form>
{% endblock %}
```

### `quizzes/templates/quizzes/attempt_result.html`

Підсумкова оцінка та розбір відповідей.

```html
{% extends "base.html" %}

{% block title %}Result: {{ attempt.quiz.title }}{% endblock %}

{% block content %}
<h1>Result: {{ attempt.quiz.title }}</h1>

<ul>
    <li>Score: {{ attempt.score }}%</li>
    <li>Correct: {{ attempt.correct_answers }} out of {{ attempt.total_questions }}</li>
    <li>Incorrect: {{ attempt.wrong_answers }}</li>
    <li>Points: {{ attempt.earned_points }} out of {{ attempt.total_points }}</li>
    <li>Started: {{ attempt.started_at }}</li>
    <li>Completed: {{ attempt.completed_at }}</li>
</ul>

<h2>Review</h2>
{% for item in review %}
    <div>
        <h3>
            {{ forloop.counter }}. {{ item.aq.question.text }}
            — {% if item.aq.is_correct %}Correct{% else %}Incorrect{% endif %}
            ({{ item.aq.earned_points }}/{{ item.aq.question.points }})
        </h3>
        <ul>
            {% for row in item.answers %}
                <li>
                    {{ row.answer.text }}
                    {% if row.selected %}[Your choice]{% endif %}
                    {% if row.answer.is_correct %}[Correct answer]{% endif %}
                </li>
            {% endfor %}
        </ul>
    </div>
{% endfor %}

<p>
    <a href="{% url 'quiz_detail' attempt.quiz.slug %}">Back to Quiz</a> |
    <a href="{% url 'quiz_list' %}">All Quizzes</a>
</p>
{% endblock %}
```

### `quizzes/templates/quizzes/my_attempts.html`

Історія спроб поточного користувача.

```html
{% extends "base.html" %}

{% block title %}My Attempts{% endblock %}

{% block content %}
<h1>My Attempts</h1>

{% if attempts %}
    <table border="1" cellpadding="4">
        <tr>
            <th>Quiz</th>
            <th>Date</th>
            <th>Status</th>
            <th>Result</th>
            <th></th>
        </tr>
        {% for attempt in attempts %}
            <tr>
                <td><a href="{% url 'quiz_detail' attempt.quiz.slug %}">{{ attempt.quiz.title }}</a></td>
                <td>{{ attempt.started_at }}</td>
                <td>{{ attempt.get_status_display }}</td>
                <td>{% if attempt.status == "completed" %}{{ attempt.score }}%{% else %}—{% endif %}</td>
                <td>
                    {% if attempt.status == "completed" %}
                        <a href="{% url 'attempt_result' attempt.pk %}">View</a>
                    {% elif attempt.status == "in_progress" %}
                        <a href="{% url 'attempt_take' attempt.pk %}">Continue</a>
                    {% endif %}
                </td>
            </tr>
        {% endfor %}
    </table>
{% else %}
    <p>No attempts yet.</p>
{% endif %}
{% endblock %}
```

## 7. Створіть таблиці та обліковий запис адміністратора

У `config/settings.py` застосунок уже доданий до `INSTALLED_APPS`. Якщо його прибрати, Django не знайде моделі `quizzes`.

Міграції — версії структури бази. Згенеруйте початкову міграцію з моделей, застосуйте її та вбудовані міграції авторизації й адмінки:

```bash
python manage.py makemigrations quizzes
python manage.py migrate
python manage.py createsuperuser
```

Введіть ім’я та пароль. Не припускайте, що користувач матиме `id=1`: ключ створює база. Увійдіть у `/admin/` і створіть категорію, тест, питання й відповіді. В тесті встановіть статус `Published`, інакше каталог його приховає. Автором оберіть створеного адміністратора. Створіть до кожного питання щонайменше два варіанти й позначте правильний. Для `single` має бути одна правильна відповідь; для `multiple` — одна чи більше. Обмеження часу задається хвилинами, порожнє поле означає без ліміту.

## 8. Запуск сервера

Перевірте конфігурацію і запустіть локальний сервер:

```bash
python manage.py check
python manage.py runserver
```

Відкрийте `http://127.0.0.1:8000/` для каталогу та `http://127.0.0.1:8000/admin/` для адмінки. `runserver` призначений для розробки. Зупиніть його `Ctrl+C`.

## 9. Тестування

Виконайте сценарій у браузері:

1. В адмінці створіть опублікований тест із двома питаннями (одне одиночне, одне множинне).
2. Зареєструйте звичайного користувача на `/register/`.
3. Перевірте каталог і фільтр категорій, відкрийте тест і почніть спробу.
4. Надішліть правильні та неправильні відповіді; перевірте відсоток, бали та розбір.
5. Відкрийте `/my-attempts/`, поверніться на результат і перевірте доступ лише власнику спроби.
6. Змініть статус іншого тесту на чернетку й переконайтеся, що його немає у каталозі.

Для запуску автоматичного тестового набору:

```bash
python manage.py test
```

У `quizzes/tests.py` реалізовано `QuizFlowTests` із вісьмома тестами. Django `TestCase` автоматично готує й очищає окрему тестову базу; реальна `db.sqlite3` не використовується. `setUp()` щоразу створює автора, двох користувачів, опублікований і чернетковий тести, питання та відповіді. `self.client` імітує HTTP-запити, `reverse()` будує URL за іменем маршруту, а `force_login()` встановлює тестову сесію без проходження форми входу.

Перевірки покривають: відображення опублікованого тесту й приховування чернетки; вимогу входу для старту; повний правильний прохід і 100%; строгий збіг множинної відповіді (неповний вибір вважається неправильним); відкидання відповіді, що належить іншому питанню, та прийняття пропуску; заборону перегляду чужої спроби; прострочену спробу зі статусом abandoned; реєстрацію та доступ до сторінки історії.

Успішний вивід завершується `OK` і містить рядок `Ran 8 tests`; кількість може змінитися, якщо ви додасте власні тести. Ці перевірки покривають ключовий потік, але не кожен крайовий випадок: наприклад, тест реєстрації перевіряє редирект і доступність сторінки історії, але не окремо перевіряє створення нового запису користувача; також не перевірено методи адмінки, відновлення активної спроби чи кожну помилкову форму.

## 10. Поширені помилки

- `No module named django`: активуйте `.venv`, встановіть залежності з requirements.txt.
- `no such table`: виконайте `makemigrations quizzes` і `migrate`.
- Шаблон не знайдено: звірте шлях, наприклад `quizzes/templates/quizzes/quiz_list.html`, та `APP_DIRS=True`.
- Тест відсутній: перевірте статус `Published` і наявність питань.
- CSRF 403: використовуйте форму сторінки та не видаляйте `{% csrf_token %}` із POST-форм.
- Адмін-посилання відсутнє: увійдіть як superuser/staff.
- Не те середовище: переконайтеся, що видно `(.venv)` і працює `python -m django --version`.

## 11. Безпека і розвиток

`SECRET_KEY` і `DEBUG=True` у налаштуваннях — лише для локального навчання. Для публічного розгортання зберігайте секрет у змінній середовища, вимкніть DEBUG, налаштуйте `ALLOWED_HOSTS` і HTTPS. Не додавайте приватні дані з локальної бази до репозиторію. Подальші навчальні кроки: розширити автоматичні тести на решту крайових випадків, додати CSS, пагінацію та підготувати розгортання.
