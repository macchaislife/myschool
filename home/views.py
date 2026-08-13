from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Opinion,
    OpinionLike,
    StudentID,
    Survey,
    SurveyQuestion,
    SurveyResponse,
    Choice,
    SurveyAnswer,
    LessonQuestion,
)

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

import json


# =====================================================
# トップページ
# =====================================================
def index(request):

    if not request.session.get("student_id"):
        return redirect("login_student")

    opinions = Opinion.objects.order_by("-created_at")[:5]
    questions = LessonQuestion.objects.order_by("-created_at")[:5]

    return render(
        request,
        "home/index.html",
        {
            "opinions": opinions,
            "questions": questions,
        }
    )


def about(request):
    return render(request, "home/about.html")


# =====================================================
# 生徒ログイン
# =====================================================
@csrf_exempt
def login_student(request):

    if request.method == "POST":

        code = request.POST.get("student_code")

        student = StudentID.objects.filter(
            student_id=code
        ).first()

        if student:
            request.session["student_id"] = student.id
            return redirect("index")

        return render(
            request,
            "home/login.html",
            {
                "error": "この生徒IDは存在しません。"
            }
        )

    return render(request, "home/login.html")


# =====================================================
# 意見投稿
# =====================================================
def post_opinion(request):

    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("login_student")

    student = StudentID.objects.filter(
        id=student_id
    ).first()

    if request.method == "POST":

        last = Opinion.objects.filter(
            student=student
        ).order_by("-created_at").first()

        if last:
            if (
                last.title == request.POST.get("title")
                and last.content == request.POST.get("content")
                and last.category == request.POST.get("category")
            ):
                return redirect("opinion_thanks")

        Opinion.objects.create(
            student=None if request.POST.get("anonymous") else student,
            category=request.POST.get("category"),
            title=request.POST.get("title"),
            content=request.POST.get("content"),
            is_anonymous=bool(request.POST.get("anonymous")),
        )

        return redirect("opinion_thanks")
        

    return render(request, "home/post_opinion.html")


def thanks(request):
    return render(request, "home/thanks.html")

def opinion_thanks(request):
    return render(request, "home/opinion_thanks.html")


def opinion_list(request):

    opinions = Opinion.objects.all().order_by("-created_at")

    for opinion in opinions:

        opinion.grade = None
        opinion.class_num = None
        opinion.number = None

        if opinion.student:
            parts = opinion.student.student_id.split("-")

            if len(parts) == 3:
                opinion.grade = parts[0]
                opinion.class_num = parts[1]
                opinion.number = parts[2]

    return render(
        request,
        "home/opinion_list.html",
        {
            "opinions": opinions
        }
    )


def opinion_detail(request, opinion_id):

    opinion = get_object_or_404(
        Opinion,
        id=opinion_id
    )

    # 意見投稿者
    grade = class_num = number = None

    if opinion.student:
        parts = opinion.student.student_id.split("-")

        if len(parts) == 3:
            grade = parts[0]
            class_num = parts[1]
            number = parts[2]

    # コメント投稿者
    comments = opinion.comments.all().order_by("created_at")

    for comment in comments:

        comment.grade = None
        comment.class_num = None
        comment.number = None

        if comment.student:
            parts = comment.student.student_id.split("-")

            if len(parts) == 3:
                comment.grade = parts[0]
                comment.class_num = parts[1]
                comment.number = parts[2]

    return render(
        request,
        "home/opinion_detail.html",
        {
            "opinion": opinion,
            "grade": grade,
            "class_num": class_num,
            "number": number,
            "comments": comments,
        }
    )


# =====================================================
# 管理者専用 意見一覧
# =====================================================
@login_required
def opinion_admin_list(request):

    if not request.user.is_staff:
        return HttpResponseForbidden(
            "このページを見る権限がありません"
        )

    opinions = Opinion.objects.all().order_by("-created_at")

    return render(
        request,
        "home/opinion_admin_list.html",
        {
            "opinions": opinions
        }
    )


# =====================================================
# アンケート
# =====================================================
def survey_list(request):

    if not request.session.get("student_id"):
        return redirect("login_student")

    surveys = Survey.objects.filter(
        is_public=True
    ).order_by("-created_at")

    return render(
        request,
        "home/survey_list.html",
        {
            "surveys": surveys
        }
    )


def survey_detail(request, survey_id):

    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("login_student")

    student = get_object_or_404(
        StudentID,
        id=student_id
    )

    survey = get_object_or_404(
        Survey,
        id=survey_id
    )

    questions = survey.questions.all()

    # 二重回答防止
    if SurveyResponse.objects.filter(
        student=student,
        survey=survey
    ).exists():

        return redirect("survey_already")

    # 回答送信
    if request.method == "POST":

        SurveyResponse.objects.create(
            student=student,
            survey=survey
        )

        for q in questions:

            value = request.POST.get(f"q_{q.id}")

            # 記述式
            if q.q_type == "text":

                SurveyAnswer.objects.create(
                    question=q,
                    student=student,
                    answer_text=value
                )

            # 選択式
            else:

                choice = Choice.objects.filter(
                    id=value
                ).first()

                SurveyAnswer.objects.create(
                    question=q,
                    student=student,
                    selected_choice=choice
                )

        return redirect("survey_thanks")

    return render(
        request,
        "home/survey_detail.html",
        {
            "survey": survey,
            "questions": questions
        }
    )


def survey_thanks(request):
    return render(request, "home/survey_thanks.html")


def survey_already(request):
    return render(request, "home/survey_already.html")


# =====================================================
# 管理者専用 アンケート結果
# =====================================================
@login_required
def survey_results(request, survey_id):

    # 管理者以外禁止
    if not request.user.is_staff:
        return HttpResponseForbidden(
            "このページを見る権限がありません"
        )

    survey = get_object_or_404(
        Survey,
        id=survey_id
    )

    questions = survey.questions.all()

    results = []

    for q in questions:

        # 選択式
        if q.q_type == "choice":

            labels = []
            counts = []

            for c in q.choices.all():

                labels.append(c.text)

                count = SurveyAnswer.objects.filter(
                    question=q,
                    selected_choice=c
                ).count()

                counts.append(count)

            results.append({
                "question": q.text,
                "type": "choice",
                "labels": labels,
                "counts": counts,
            })

        # 自由記述
        else:

            texts = list(
                SurveyAnswer.objects.filter(
                    question=q
                ).values_list(
                    "answer_text",
                    flat=True
                )
            )

            results.append({
                "question": q.text,
                "type": "text",
                "texts": texts,
            })

    return render(
        request,
        "home/survey_results.html",
        {
            "survey": survey,
            "results_json": json.dumps(
                results,
                ensure_ascii=False
            ),
        }
    )


# =====================================================
# 授業への質問
# =====================================================
def post_lesson_question(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        LessonQuestion.objects.create(
            title=title,
            content=content,
            subject="その他"
        )

        return redirect("lesson_question_list")

    return render(
        request,
        "home/post_lesson_question.html"
    )


def lesson_question_list(request):

    questions = LessonQuestion.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "home/lesson_question_list.html",
        {
            "questions": questions
        }
    )


def lesson_question_student_detail(
    request,
    question_id
):

    question = get_object_or_404(
        LessonQuestion,
        id=question_id
    )

    return render(
        request,
        "home/lesson_question_detail_student.html",
        {
            "question": question
        }
    )

def opinion_like(request, opinion_id):

    if request.method != "POST":
        return redirect("opinion_detail", opinion_id=opinion_id)

    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("login_student")

    student = StudentID.objects.filter(
        id=student_id
    ).first()

    if not student:
        return redirect("login_student")

    opinion = get_object_or_404(
        Opinion,
        id=opinion_id
    )

    like = OpinionLike.objects.filter(
        opinion=opinion,
        student=student
    ).first()

    if like:
        # すでにいいねしていたら取り消す
        like.delete()
    else:
        # まだいいねしていなければ追加
        OpinionLike.objects.create(
            opinion=opinion,
            student=student
        )

    return redirect(
        "opinion_detail",
        opinion_id=opinion_id
    )

# =====================================================
# 管理者専用 質問詳細
# =====================================================
@login_required
def lesson_question_detail(
    request,
    question_id
):

    if not request.user.is_staff:
        return HttpResponseForbidden(
            "このページを見る権限がありません"
        )

    question = get_object_or_404(
        LessonQuestion,
        id=question_id
    )

    if request.method == "POST":

        question.answer = request.POST.get("answer")
        question.answered_at = timezone.now()
        question.is_answered = True

        question.save()

        return redirect("teacher_dashboard")

    return render(
        request,
        "home/lesson_question_detail.html",
        {
            "question": question
        }
    )

# =====================================================
# 管理者ダッシュボード
# =====================================================
@login_required
def teacher_dashboard(request):

    if not request.user.is_staff:
        return HttpResponseForbidden(
            "このページを見る権限がありません"
        )

    return render(
        request,
        "home/teacher_dashboard.html",
        {
            "lesson_questions": LessonQuestion.objects.all().order_by("-created_at")[:5],
            "opinions": Opinion.objects.all().order_by("-created_at")[:5],
            "surveys": Survey.objects.all().order_by("-created_at"),
        }
    )


# =====================================================
# 管理者作成（1回だけ）
# =====================================================
def create_admin(request):

    User = get_user_model()

    if not User.objects.filter(
        username="admin"
    ).exists():

        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="20209304"
        )

        return HttpResponse("admin created")

    return HttpResponse("already exists")

def opinion_comment(request, opinion_id):

    if request.method != "POST":
        return redirect(
            "opinion_detail",
            opinion_id=opinion_id
        )

    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("login_student")

    student = StudentID.objects.filter(
        id=student_id
    ).first()

    if not student:
        return redirect("login_student")

    opinion = get_object_or_404(
        Opinion,
        id=opinion_id
    )

    content = request.POST.get("content", "").strip()

    if not content:
        return redirect(
            "opinion_detail",
            opinion_id=opinion_id
        )

    OpinionComment.objects.create(
        opinion=opinion,
        student=student,
        content=content,
        is_anonymous=False,
    )

    return redirect(
        "opinion_detail",
        opinion_id=opinion_id
    )