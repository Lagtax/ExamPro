from django.urls import path
from .admin_views import (
    admin_exam_list,
    admin_create_exam,
    admin_update_exam,
    admin_delete_exam,
    admin_question_list,
    admin_create_question,
    admin_update_question,
    admin_delete_question
)

urlpatterns = [
    path('exams/', admin_exam_list, name='admin_exam_list'),
    path('exams/create/', admin_create_exam, name='admin_create_exam'),
    path('exams/<int:exam_id>/update/', admin_update_exam, name='admin_update_exam'),
    path('exams/<int:exam_id>/delete/', admin_delete_exam, name='admin_delete_exam'),
    path('exams/<int:exam_id>/questions/', admin_question_list, name='admin_question_list'),
    path('exams/<int:exam_id>/questions/create/', admin_create_question, name='admin_create_question'),
    path('questions/<int:question_id>/update/', admin_update_question, name='admin_update_question'),
    path('questions/<int:question_id>/delete/', admin_delete_question, name='admin_delete_question'),
]