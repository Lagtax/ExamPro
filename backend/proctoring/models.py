from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from exams.models import Exam

class ProctorLog(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    event = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
