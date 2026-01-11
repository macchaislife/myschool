from django.contrib import admin
from .models import StudentID, Opinion, Survey, SurveyQuestion, SurveyAnswer, Choice

# ------------------------------
# StudentID（生徒）
# ------------------------------
@admin.register(StudentID)
class StudentIDAdmin(admin.ModelAdmin):
    list_display = ("student_id", "grade", "class_num", "number", "created_at")
    list_filter = ("grade", "class_num")
    search_fields = ("student_id", "grade", "class_num", "number")
    ordering = ("grade", "class_num", "number")


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
# Survey（アンケート本体）
# ------------------------------
@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "question_count", "answer_count", "is_public")
    list_filter = ("is_public",)
    search_fields = ("title",)
    ordering = ("-created_at",)

    # 質問数
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = "質問数"

    # 回答数
    def answer_count(self, obj):
        return SurveyAnswer.objects.filter(survey=obj).count()
    answer_count.short_description = "回答数"


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
    list_display = ("survey", "question", "student", "short_answer", "created_at")
    list_filter = ("survey", "student")
    search_fields = ("answer_text", "student__student_id")
    ordering = ("-created_at",)

    # 管理画面で長文が見やすくなるために短縮
    def short_answer(self, obj):
        return obj.answer_text[:30] + ("..." if len(obj.answer_text) > 30 else "")
    short_answer.short_description = "回答（短縮版）"

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "question")
    list_filter = ("question",)