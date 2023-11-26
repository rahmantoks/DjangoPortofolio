from django.urls import path
from . import views

urlpatterns = [
    path('snake/', views.snake)
]