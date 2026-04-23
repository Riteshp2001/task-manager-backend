from django.urls import path

from . import views

urlpatterns = [
    path('evaluate-overdue/', views.evaluate_overdue, name='evaluate_overdue'),
    path('validate-transition/', views.validate_transition, name='validate_transition'),
]
