# users/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10)  # student / admin
    class_name = models.CharField(max_length=20)
    batch = models.CharField(max_length=20)
