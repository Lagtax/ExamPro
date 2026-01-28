from django.urls import path
from .views import log_event, get_violations

urlpatterns = [
    path('log/', log_event, name='log_event'),
    path('violations/', get_violations, name='get_violations'),
]