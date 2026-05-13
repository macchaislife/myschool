from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # トップページ
    path("", views.index, name="index"),

    # ログイン
    path("login/", views.login_student, name="login_student"),

    # アンケート
    path("surveys/", views.survey_list, name="survey_list"),
    path("surveys/<int:survey_id>/", views.survey_detail, name="survey_detail"),
    path("surveys/<int:survey_id>/results/", views.survey_results, name="survey_results"),
    path("survey/thanks/", views.survey_thanks, name="survey_thanks"),
    path("survey/already/", views.survey_already, name="survey_already"),

    # 意見投稿
    path("opinion/post/", views.post_opinion, name="post_opinion"),
    path("opinion/thanks/", views.opinion_thanks, name="opinion_thanks"),

    # 授業質問
    path("lesson/question/", views.post_lesson_question, name="post_lesson_question"),
    path("lesson/questions/", views.lesson_question_list, name="lesson_question_list"),
    path(
        "lesson/question/<int:question_id>/",
        views.lesson_question_student_detail,
        name="lesson_question_student_detail"
    ),

    # 管理者
    path("admin/opinions/", views.opinion_admin_list, name="opinion_admin_list"),
    path("admin/dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path(
        "admin/lesson-question/<int:question_id>/",
        views.lesson_question_detail,
        name="lesson_question_detail"
    ),

    path(
    "teacher/login/",
    auth_views.LoginView.as_view(
        template_name="home/teacher_login.html"
    ),
    name="teacher_login"
),

    # 管理者作成
    path("create-admin/", views.create_admin, name="create_admin"),
]