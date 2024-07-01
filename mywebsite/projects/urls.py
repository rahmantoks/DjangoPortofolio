from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.projects_main_page, name = 'projects_main_page'),
    path('projects/<slug>/', views.project, name = 'project'),
]