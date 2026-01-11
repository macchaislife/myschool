from django.urls import path
from . import views

urlpatterns = [
    # 生徒ログイン
    path("login/", views.login_student, name="login_student"),
    path("", views.login_student, name="login"),

    # アンケート
    path("surveys/", views.survey_list, name="survey_list"),
    path("surveys/<int:survey_id>/", views.survey_detail, name="survey_detail"),
    path("surveys/<int:survey_id>/results/", views.survey_results, name="survey_results"),
    path("survey/thanks/", views.survey_thanks, name="survey_thanks"),
    path("survey/already/", views.survey_already, name="survey_already"),

    # 授業への質問（STEP1）
    path("lesson/question/", views.post_lesson_question, name="post_lesson_question"),

    # 意見・要望（STEP2）
    path("opinion/post/", views.post_opinion, name="post_opinion"),

    # 管理者用
    path("admin/opinions/", views.opinion_admin_list, name="opinion_admin_list"),
    path("admin/dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path(
    "admin/lesson-question/<int:question_id>/",
    views.lesson_question_detail,
    name="lesson_question_detail"
),

path(
    "lesson/question/<int:question_id>/",
    views.lesson_question_student_detail,
    name="lesson_question_student_detail"
),

]