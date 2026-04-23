from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('', views.project_list_create, name='project_list_create'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
]