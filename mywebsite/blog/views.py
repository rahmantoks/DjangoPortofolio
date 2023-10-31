from django.shortcuts import render
from .models import Post, Category, Author

# Create your views here.
def homepage(request):
    categories = Category.objects.all()[0:3]
    latest = Post.objects.order_by('-timestamp')[0:3]
    context = {
        'object_list' : latest,
        'categories' : categories,
    }
    return render(request, 'homepage.html', context)

def post(request,slug):
    post = Post.objects.get(slug=slug)
    context = {
        'post' : post,
    }
    return render(request, 'post.html', context)

def category_post_list(request, slug):
    category = Category.objects.get(slug=slug)
    posts = Post.objects.filter(categories__in=[category])
    context = {
        'posts' : posts,
    }
    return render(request, 'post_list.html', context)

def all_posts(request):
    posts = Post.objects.order_by('-timestamp')
    context = {
        'posts' : posts,
    }
    return render(request, 'all_posts.html', context)