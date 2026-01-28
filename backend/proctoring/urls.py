from django.urls import path
from .views import log_event

urlpatterns = [
    path('log/', log_event),
]
