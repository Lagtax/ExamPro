# exams/teacher_urls.py
from django.urls import path
from .teacher_views import (
    teacher_exam_list,
    teacher_create_exam,
    teacher_update_exam,
    teacher_delete_exam,
    teacher_student_performance,
)
from .admin_views import (
    admin_question_list,
    admin_create_question,
    admin_update_question,
    admin_delete_question,
)

urlpatterns = [
    # Exam Management
    path('exams/', teacher_exam_list, name='teacher_exam_list'),
    path('exams/create/', teacher_create_exam, name='teacher_create_exam'),
    path('exams/<int:exam_id>/update/', teacher_update_exam, name='teacher_update_exam'),
    path('exams/<int:exam_id>/delete/', teacher_delete_exam, name='teacher_delete_exam'),
    
    # Question Management 
    path('exams/<int:exam_id>/questions/', admin_question_list, name='teacher_question_list'),
    path('exams/<int:exam_id>/questions/create/', admin_create_question, name='teacher_create_question'),
    path('questions/<int:question_id>/update/', admin_update_question, name='teacher_update_question'),
    path('questions/<int:question_id>/delete/', admin_delete_question, name='teacher_delete_question'),
    
    # Student Performance
    path('performance/', teacher_student_performance, name='teacher_student_performance'),
]