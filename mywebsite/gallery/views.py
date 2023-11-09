from django.shortcuts import render
from .models import Image

# Create your views here.
def gallery(request):
    images = Image.objects.all()
    context = {
        'image_list' : images,
    }

    return render(request, 'gallery.html',context)