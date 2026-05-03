# models.py

from django.db import models
from django.contrib.auth.models import User


# =========================
# プロフィール
# =========================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30)

    def __str__(self):
        return self.nickname


# =========================
# 生徒ID
# =========================
class StudentID(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    number = models.PositiveIntegerField(unique=True)
    student_id = models.CharField(max_length=10, unique=True)
    is_graduated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = f"S{self.number:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.student_id


# =========================
# 所属クラス
# =========================
class StudentEnrollment(models.Model):
    student = models.ForeignKey(StudentID, on_delete=models.CASCADE)
    school_year = models.IntegerField()
    grade = models.PositiveSmallIntegerField()
    class_num = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("student", "school_year")

    def __str__(self):
        return f"{self.school_year}年 {self.grade}-{self.class_num}"


# =========================
# 意見投稿
# =========================
class Opinion(models.Model):
    CATEGORY_CHOICES = [
        ("lesson", "授業"),
        ("facility", "施設"),
        ("event", "行事"),
        ("rules", "校則"),
        ("other", "その他"),
    ]

    student = models.ForeignKey(
        StudentID,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# アンケート
# =========================
class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SurveyQuestion(models.Model):
    QUESTION_TYPE = [
        ("text", "自由入力"),
        ("choice", "選択式"),
    ]

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    text = models.CharField(max_length=300)
    q_type = models.CharField(max_length=10, choices=QUESTION_TYPE)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(
        SurveyQuestion,
        on_delete=models.CASCADE,
        related_name="choices"
    )
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text


# 回答内容
class SurveyAnswer(models.Model):
    student = models.ForeignKey(StudentID, on_delete=models.CASCADE)
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.question}"


# 回答済み判定
class SurveyResponse(models.Model):
    student = models.ForeignKey(StudentID, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("student", "survey")

    def __str__(self):
        return f"{self.student} - {self.survey}"


# =========================
# 授業質問
# =========================
class LessonQuestion(models.Model):
    CATEGORY_CHOICES = [
        ("math", "数学"),
        ("english", "英語"),
        ("science", "理科"),
        ("social", "社会"),
        ("other", "その他"),
    ]

    student = models.ForeignKey(
        StudentID,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    content = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        return self.title