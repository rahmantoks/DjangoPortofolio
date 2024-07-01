from django.shortcuts import render
from .models import Project

# Create your views here.
def projects_main_page(request):
    projects = Project.objects.all()
    context = {
        'projects' : projects,
    }
    return render(request, 'projects_main_page.html', context)

def project(request,slug):
    project = Project.objects.get(slug=slug)
    context = {
        'project' : project,
    }
    return render(request, 'project.html', context)