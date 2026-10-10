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
