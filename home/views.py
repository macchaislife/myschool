from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Opinion, StudentID,
    Survey, SurveyQuestion, SurveyResponse, Choice, SurveyAnswer,
    LessonQuestion
)
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
import json


# =====================================================
# トップページ
# =====================================================
def index(request):
    return render(request, "home/index.html")


def about(request):
    return render(request, "home/about.html")


# =====================================================
# 意見投稿機能
# =====================================================
def post_opinion(request):
    student_id = request.session.get("student_id")
    student = StudentID.objects.filter(id=student_id).first()

    if request.method == "POST":
        Opinion.objects.create(
            student=None if request.POST.get("anonymous") else student,
            category=request.POST.get("category"),
            title=request.POST.get("title"),
            content=request.POST.get("content"),
            image=request.FILES.get("image"),
            is_anonymous=bool(request.POST.get("anonymous")),
        )
        return redirect("thanks")

    return render(request, "home/post_opinion.html")


def thanks(request):
    return render(request, "home/thanks.html")


def opinion_list(request):
    opinions = Opinion.objects.all().order_by("-created_at")
    return render(request, "home/opinion_list.html", {"opinions": opinions})


def opinion_detail(request, opinion_id):
    opinion = get_object_or_404(Opinion, id=opinion_id)
    return render(request, "home/opinion_detail.html", {"opinion": opinion})


def opinion_admin_list(request):
    opinions = Opinion.objects.all().order_by("-created_at")
    return render(request, "home/opinion_admin_list.html", {
        "opinions": opinions
    })


# =====================================================
# アンケート機能
# =====================================================
def survey_list(request):
    surveys = Survey.objects.filter(is_public=True).order_by("-created_at")
    return render(request, "home/survey_list.html", {"surveys": surveys})


def login_student(request):
    if request.method == "POST":
        code = request.POST.get("code")
        student = StudentID.objects.filter(student_id=code).first()

        if student:
            request.session["student_id"] = student.id
            return redirect("survey_list")

        return render(request, "home/login.html", {"error": "この生徒IDは存在しません。"})

    return render(request, "home/login.html")


def survey_detail(request, survey_id):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("login_student")

    student = get_object_or_404(StudentID, id=student_id)
    survey = get_object_or_404(Survey, id=survey_id)
    questions = survey.questions.all()

    if SurveyResponse.objects.filter(student=student, survey=survey).exists():
        return redirect("survey_already")

    if request.method == "POST":
        SurveyResponse.objects.create(student=student, survey=survey)

        for q in questions:
            value = request.POST.get(f"q_{q.id}")

            if q.q_type == "text":
                SurveyAnswer.objects.create(
                    survey=survey,
                    question=q,
                    student=student,
                    answer_text=value
                )
            else:
                choice = Choice.objects.filter(id=value).first()
                SurveyAnswer.objects.create(
                    survey=survey,
                    question=q,
                    student=student,
                    selected_choice=choice
                )

        return redirect("survey_thanks")

    return render(request, "home/survey_detail.html", {
        "survey": survey,
        "questions": questions
    })


def survey_thanks(request):
    return render(request, "home/survey_thanks.html")


def survey_already(request):
    return render(request, "home/survey_already.html")


@staff_member_required
def survey_results(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    questions = survey.questions.all()

    results = []

    for q in questions:
        if q.q_type == "choice":
            labels = []
            counts = []

            for c in q.choices.all():
                labels.append(c.text)
                counts.append(
                    SurveyAnswer.objects.filter(
                        question=q,
                        selected_choice=c
                    ).count()
                )

            results.append({
                "question": q.text,
                "type": "choice",
                "labels": labels,
                "counts": counts,
            })

        else:
            texts = list(
                SurveyAnswer.objects.filter(question=q)
                .values_list("answer_text", flat=True)
            )

            results.append({
                "question": q.text,
                "type": "text",
                "texts": texts,
            })

    return render(request, "home/survey_results.html", {
        "survey": survey,
        "results_json": json.dumps(results, ensure_ascii=False),
    })


# =====================================================
# 授業への質問機能
# =====================================================
def post_lesson_question(request):
    student_id = request.session.get("student_id")
    student = StudentID.objects.filter(id=student_id).first()

    if request.method == "POST":
        LessonQuestion.objects.create(
            student=None if request.POST.get("anonymous") else student,
            category=request.POST.get("category"),
            subject=request.POST.get("subject"),
            title=request.POST.get("title"),
            content=request.POST.get("content"),
            is_anonymous=bool(request.POST.get("anonymous")),
        )
        return redirect("lesson_question_list")

    return render(request, "home/post_lesson_question.html")


def lesson_question_list(request):
    category = request.GET.get("category")

    questions = LessonQuestion.objects.all().order_by("-created_at")
    if category:
        questions = questions.filter(category=category)

    return render(request, "home/lesson_question_list.html", {
        "questions": questions
    })


def lesson_question_student_detail(request, question_id):
    question = get_object_or_404(LessonQuestion, id=question_id)
    return render(request, "home/lesson_question_detail.html", {
        "question": question
    })


@staff_member_required
def lesson_question_detail(request, question_id):
    question = get_object_or_404(LessonQuestion, id=question_id)

    if request.method == "POST":
        question.answer = request.POST.get("answer")
        question.answered_at = timezone.now()
        question.save()
        return redirect("teacher_dashboard")

    return render(request, "home/lesson_question_detail.html", {
        "question": question
    })


@staff_member_required
def teacher_dashboard(request):
    return render(request, "home/teacher_dashboard.html", {
        "lesson_questions": LessonQuestion.objects.all().order_by("-created_at")[:5],
        "opinions": Opinion.objects.all().order_by("-created_at")[:5],
        "surveys": Survey.objects.all().order_by("-created_at"),
    })