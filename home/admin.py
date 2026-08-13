from django.contrib import admin
from .models import (
    StudentID,
    StudentEnrollment,
    Opinion,
    OpinionComment,
    Survey,
    SurveyQuestion,
    SurveyAnswer,
    Choice,
    LessonQuestion,
)

# ------------------------------
# StudentID（生徒）
# ------------------------------
@admin.register(StudentID)
class StudentIDAdmin(admin.ModelAdmin):
    list_display = (
        "student_id",
        "number",
        "is_graduated",
        "created_at",
    )

    list_filter = (
        "is_graduated",
    )

    search_fields = ("student_id",)
    ordering = ("number",)

    actions = ["mark_as_graduated"]

    def mark_as_graduated(self, request, queryset):
        queryset.update(is_graduated=True)

    mark_as_graduated.short_description = "選択した生徒を卒業にする"


# ------------------------------
# StudentEnrollment（学年管理）
# ------------------------------
@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "school_year", "grade", "class_num")
    list_filter = ("school_year", "grade", "class_num")
    ordering = ("school_year", "grade", "class_num")


# ------------------------------
# Opinion（意見箱）
# ------------------------------
@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = ("student", "category", "created_at")
    list_filter = ("category",)
    search_fields = ("content", "student__student_id")
    ordering = ("-created_at",)

# ------------------------------
# OpinionComment（意見へのコメント）
# ------------------------------
@admin.register(OpinionComment)
class OpinionCommentAdmin(admin.ModelAdmin):
    list_display = (
        "opinion",
        "student",
        "content",
        "is_anonymous",
        "created_at",
    )

    list_filter = (
        "is_anonymous",
        "created_at",
    )

    search_fields = (
        "content",
        "student__student_id",
        "opinion__title",
    )

    ordering = ("-created_at",)


# ------------------------------
# Survey（アンケート本体）
# ------------------------------
@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "is_public")
    list_filter = ("is_public",)
    search_fields = ("title",)
    ordering = ("-created_at",)


# ------------------------------
# SurveyQuestion（質問）
# ------------------------------
@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "survey", "q_type")
    list_filter = ("survey", "q_type")
    search_fields = ("text",)
    ordering = ("survey",)


# ------------------------------
# SurveyAnswer（回答）
# ------------------------------
@admin.register(SurveyAnswer)
class SurveyAnswerAdmin(admin.ModelAdmin):
    list_display = ("student", "question", "short_answer", "created_at")
    list_filter = ("student",)
    search_fields = ("answer_text", "student__student_id")
    ordering = ("-created_at",)

    def short_answer(self, obj):
        if obj.answer_text:
            return obj.answer_text[:30] + ("..." if len(obj.answer_text) > 30 else "")
        if obj.selected_choice:
            return obj.selected_choice.text
        return "-"
    short_answer.short_description = "回答"


# ------------------------------
# Choice
# ------------------------------
@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "question")
    list_filter = ("question",)


# ------------------------------
# LessonQuestion（授業への質問）
# ------------------------------
@admin.register(LessonQuestion)
class LessonQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "subject",
        "is_answered",
        "created_at",
    )

    list_filter = (
        "subject",
        "is_answered",
    )

    search_fields = (
        "title",
        "content",
    )

    ordering = ("-created_at",)