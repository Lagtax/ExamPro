from django.db import models
from users.models import UserProfile


class Exam(models.Model):
    title = models.CharField(max_length=100)
    duration = models.IntegerField()  # in minutes
    allowed_class = models.CharField(max_length=20)
    allowed_batch = models.CharField(max_length=20)

    def __str__(self):
        return self.title
    
    @property
    def total_marks(self):
        """Calculate total marks based on number of questions"""
        return self.question_set.count()


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1)

    def __str__(self):
        return self.question_text


class ExamAttempt(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    is_submitted = models.BooleanField(default=False)
    violation_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('student', 'exam')
        

class Answer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)