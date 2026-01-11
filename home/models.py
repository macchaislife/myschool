from django.db import models

from django.db import models

class StudentID(models.Model):
    grade = models.PositiveSmallIntegerField()
    class_num = models.PositiveSmallIntegerField()
    number = models.PositiveSmallIntegerField()
    student_id = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = f"{self.grade}-{self.class_num}-{self.number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.student_id

class Opinion(models.Model):
    CATEGORY_CHOICES = [
        ('lesson', '授業について'),
        ('facility', '施設について'),
        ('event', '行事について'),
        ('rules', '校則について'),
        ('other', 'その他'),
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
    image = models.ImageField(upload_to='opinions/', blank=True, null=True)
    is_anonymous = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    # --- アンケート（Survey）機能 ここから ---
class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)  # 公開・非公開
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SurveyQuestion(models.Model):

    QUESTION_TYPE = [
        ("text", "自由入力"),
        ("choice", "選択式"),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=300)
    q_type = models.CharField(max_length=10, choices=QUESTION_TYPE, default="text")

    def __str__(self):
        return f"{self.survey.title} - {self.text}"

class SurveyAnswer(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    student = models.ForeignKey('StudentID', on_delete=models.CASCADE)

    # 自由入力・選択式両対応
    answer_text = models.TextField(blank=True, null=True)
    selected_choice = models.ForeignKey('home.Choice', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question.text} の回答"
    
class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    student_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.student_id} の回答 - {self.survey.title}"
    
# ▼ 選択肢（選択式質問の場合のみ）
class Choice(models.Model):
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.question.text} - {self.text}"

# --- アンケート機能 ここまで ---

class SurveyResponse(models.Model):
    student = models.ForeignKey(StudentID, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "survey"],
                name="unique_student_survey"
            )
        ]

class LessonQuestion(models.Model):
    SUBJECT_CHOICES = [
        ("math", "数学"),
        ("jp", "国語"),
        ("en", "英語"),
        ("sci", "理科"),
        ("soc", "社会"),
        ("other", "その他"),
    ]

    def is_answered(self):
        return self.answers.exists()

    student = models.ForeignKey(
        StudentID,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    answer = models.TextField(blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class LessonQuestion(models.Model):
    CATEGORY_CHOICES = [
        ("lesson", "授業"),
        ("facility", "施設"),
        ("event", "行事"),
        ("other", "その他"),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="lesson"
    )

    title = models.CharField(max_length=100)
    content = models.TextField()
    student = models.ForeignKey(
        StudentID,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)