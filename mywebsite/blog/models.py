from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_username()

class Category(models.Model):
    title = models.CharField(max_length=20)
    explanation = models.TextField()
    slug = models.SlugField()

    def __str__(self):
        return self.title

class Tag(models.Model):
    title = models.CharField(max_length=20)
    explanation = models.TextField()
    slug = models.SlugField()

    def __str__(self):
        return self.title

class Language(models.Model):
    language_id = models.CharField(max_length=2)
    language = models.CharField(max_length=20)

    def __str__(self):
        return self.language

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    overview = models.TextField()
    short = models.TextField()
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    lang = models.ForeignKey(Language,on_delete=models.CASCADE)
    featured = models.BooleanField()

    def __str__(self):
        return self.title
