from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify


User = get_user_model()

# Create your models here.
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_username()

class Category(models.Model):
    title = models.CharField(max_length=20)
    subtitle = models.CharField(max_length=20)
    slug = models.SlugField()

    def __str__(self):
        return self.title
    
class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    overview = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)
    featured = models.BooleanField()

    def __str__(self):
        return self.title
