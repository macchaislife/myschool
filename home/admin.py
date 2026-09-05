from django.contrib import admin, messages
from .models import (
    generate_initial_password,
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
        "must_change_password",
        "created_at",
    )

    list_filter = (
        "is_graduated",
        "must_change_password",
    )

    search_fields = ("student_id",)
    ordering = ("number",)

    actions = ["mark_as_graduated", "reset_password"]

    def mark_as_graduated(self, request, queryset):
        queryset.update(is_graduated=True)

    mark_as_graduated.short_description = "選択した生徒を卒業にする"

    def reset_password(self, request, queryset):
        """
        選択した生徒のパスワードをランダムな英数字で再発行する。
        新しいパスワードは画面上に一度だけ表示されるので、
        その場でメモして生徒に伝えること（DBには平文で残らない）。
        """
        lines = []

        for student in queryset:
            raw = generate_initial_password()
            student.set_password(raw)
            student.must_change_password = True
            student.save()
            lines.append(f"{student.student_id}: {raw}")

        self.message_user(
            request,
            "新しいパスワード（この場限りの表示です）　" + " ／ ".join(lines),
            level=messages.WARNING,
        )

    reset_password.short_description = "選択した生徒のパスワードを再発行する"


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