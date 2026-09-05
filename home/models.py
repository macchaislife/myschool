# models.py

import secrets
import string

from django.db import models
from django.contrib.auth.hashers import make_password, check_password as check_password_hash
from django.contrib.auth.models import User


def generate_initial_password(length=8):
    """
    ログイン用の初期パスワードをランダムな英数字で生成する。
    secrets モジュールを使うことで推測されにくい値にしている。
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


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

    # ログイン用パスワード（ハッシュ化して保存する。平文は保存しない）
    password = models.CharField(max_length=128, blank=True)

    # True の間はログイン後にパスワード変更ページへ強制的に飛ばす
    must_change_password = models.BooleanField(default=True)

    # 直近の save() で新規発行した初期パスワード（平文）を一時的に保持する。
    # DB には保存されない。呼び出し側が生成直後の1回だけ生徒に伝えるためのもの。
    _raw_initial_password = None

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        if not self.password:
            return False
        return check_password_hash(raw_password, self.password)

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = f"S{self.number:04d}"

        # 新規作成で、まだパスワードが設定されていない場合のみ
        # ランダムな初期パスワードを自動発行する。
        if self._state.adding and not self.password:
            raw = generate_initial_password()
            self.set_password(raw)
            self.must_change_password = True
            self._raw_initial_password = raw

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

class OpinionLike(models.Model):
    opinion = models.ForeignKey(
        Opinion,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    student = models.ForeignKey(
        StudentID,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["opinion", "student"],
                name="unique_opinion_like"
            )
        ]

    def __str__(self):
        return f"{self.student} → {self.opinion}"
    
class OpinionComment(models.Model):
    opinion = models.ForeignKey(
        Opinion,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    student = models.ForeignKey(
        StudentID,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    content = models.TextField()

    is_anonymous = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:30]


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

    is_answered = models.BooleanField(default=False)

    def __str__(self):
        return self.title