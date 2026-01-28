from django.urls import path
from .admin_views import (
    admin_user_list,
    admin_create_user,
    admin_update_user,
    admin_delete_user
)

urlpatterns = [
    path('users/', admin_user_list, name='admin_user_list'),
    path('users/create/', admin_create_user, name='admin_create_user'),
    path('users/<int:user_id>/update/', admin_update_user, name='admin_update_user'),
    path('users/<int:user_id>/delete/', admin_delete_user, name='admin_delete_user'),
]
