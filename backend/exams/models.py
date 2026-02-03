from django.db import models
from users.models import UserProfile
from django.utils import timezone


class Exam(models.Model):
    title = models.CharField(max_length=100)
    duration = models.IntegerField()  
    department = models.CharField(max_length=50)  
    allowed_batch = models.CharField(max_length=20, blank=True)  
    
    start_time = models.DateTimeField()  
    end_time = models.DateTimeField()  
    
    created_by = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_exams',
        limit_choices_to={'role': 'teacher'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    @property
    def total_marks(self):
        """Calculate total marks based on number of questions"""
        return self.question_set.count()
    
    @property
    def is_active(self):
        """Check if exam is currently available"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
    @property
    def is_upcoming(self):
        """Check if exam is scheduled for future"""
        return timezone.now() < self.start_time
    
    @property
    def is_expired(self):
        """Check if exam time has passed"""
        return timezone.now() > self.end_time

    class Meta:
        ordering = ['-start_time']


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1, choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ])

    def __str__(self):
        return self.question_text[:50]


class ExamAttempt(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('absent', 'Absent'),
    ]
    
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    is_submitted = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    violation_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('student', 'exam')
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.exam.title}"
        

class Answer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)

    def __str__(self):
        return f"Answer for {self.question.id}"