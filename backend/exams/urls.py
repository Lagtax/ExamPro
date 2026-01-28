from django.urls import path
from .views import *

urlpatterns = [
    path('', exam_list),
    path('<int:exam_id>/questions/', exam_questions),
    path('<int:exam_id>/start/', start_exam),
    path('<int:exam_id>/submit/', submit_exam),
    path('<int:exam_id>/result/', exam_result),
]
