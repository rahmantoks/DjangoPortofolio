from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.homepage, name = 'homepage'),
    path('blog/post/<slug>/', views.post, name = 'post'),
    path('blog/postlist/<slug>/', views.post, name = 'postlist'),
    path('blog/posts/', views.all_posts, name = 'allposts')
]