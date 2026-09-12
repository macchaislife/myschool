from django.contrib import admin, messages
from django.utils import timezone
from datetime import timedelta

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
    Report,
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
        "suspension_status",
        "created_at",
    )

    list_filter = (
        "is_graduated",
        "must_change_password",
    )

    search_fields = ("student_id",)
    ordering = ("number",)

    # password は直接編集できないようにする（平文で保存される事故を防ぐため）。
    # パスワードの設定・再発行は必ず下の「reset_password」アクションを使う。
    fields = (
        "user",
        "number",
        "student_id",
        "is_graduated",
        "password_status",
        "must_change_password",
        "suspended_until",
    )

    readonly_fields = ("password_status",)

    actions = [
        "mark_as_graduated",
        "reset_password",
        "suspend_1day",
        "suspend_7days",
        "lift_suspension",
    ]

    def password_status(self, obj):
        if obj.pk and obj.password:
            return "設定済み（変更する場合は一覧画面で選択して「パスワードを再発行する」を実行してください）"
        return "未設定（保存すると自動でランダムなパスワードが発行されます）"
    password_status.short_description = "パスワード"

    def suspension_status(self, obj):
        if obj.is_suspended():
            return f"停止中（{timezone.localtime(obj.suspended_until):%Y/%m/%d %H:%M} まで）"
        return "-"
    suspension_status.short_description = "行動停止"

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

    def _suspend_for(self, request, queryset, days):
        until = timezone.now() + timedelta(days=days)
        queryset.update(suspended_until=until)

        self.message_user(
            request,
            f"{queryset.count()}名を{until:%Y/%m/%d %H:%M}まで一時停止にしました。",
            level=messages.WARNING,
        )

    def suspend_1day(self, request, queryset):
        self._suspend_for(request, queryset, days=1)

    suspend_1day.short_description = "選択した生徒を1日間、行動停止にする"

    def suspend_7days(self, request, queryset):
        self._suspend_for(request, queryset, days=7)

    suspend_7days.short_description = "選択した生徒を7日間、行動停止にする"

    def lift_suspension(self, request, queryset):
        queryset.update(suspended_until=None)

        self.message_user(
            request,
            "選択した生徒の行動停止を解除しました。",
        )

    lift_suspension.short_description = "選択した生徒の行動停止を解除する"


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
# Report（通報）
# ------------------------------
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "target_type",
        "target_id",
        "reason",
        "reporter",
        "reported_student",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "target_type",
        "reason",
    )

    search_fields = (
        "reporter__student_id",
        "reported_student__student_id",
        "detail",
    )

    ordering = ("-created_at",)

    actions = ["mark_as_reviewed", "suspend_reported_student_7days"]

    def mark_as_reviewed(self, request, queryset):
        queryset.update(status="reviewed")

    mark_as_reviewed.short_description = "対応済みにする"

    def suspend_reported_student_7days(self, request, queryset):
        """
        選択した通報について、通報された生徒を7日間の行動停止にする。
        1つの通報に対して複数回実行しても、停止期限が延びるだけ。
        """
        until = timezone.now() + timedelta(days=7)
        suspended = []

        for report in queryset:
            student = report.reported_student

            if not student:
                continue

            student.suspended_until = until
            student.save()
            suspended.append(student.student_id)

        queryset.update(status="reviewed")

        if suspended:
            self.message_user(
                request,
                f"{'、'.join(suspended)} を{until:%Y/%m/%d %H:%M}まで行動停止にしました。",
                level=messages.WARNING,
            )
        else:
            self.message_user(
                request,
                "通報された生徒が特定できないものが含まれていました（匿名投稿など）。"
                "個別に生徒一覧から行動停止にしてください。",
                level=messages.WARNING,
            )

    suspend_reported_student_7days.short_description = (
        "通報された生徒を7日間、行動停止にする（対応済みにする）"
    )


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