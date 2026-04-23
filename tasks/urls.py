from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list_create, name='task_list_create'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('<int:task_id>/status/', views.update_task_status, name='update_task_status'),
    path('check-overdue/', views.check_and_mark_overdue, name='check_overdue'),
    path('can-change/', views.can_change_status, name='can_change_status'),
]