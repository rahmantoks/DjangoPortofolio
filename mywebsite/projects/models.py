from django.db import models
from django.utils.text import slugify
from django_resized import ResizedImageField

class ProjectImage(models.Model):
    caption = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    image = ResizedImageField(size=[1920, 1080], force_format='JPEG', upload_to="project/")
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.caption

class Project(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.CharField(max_length=100)
    image = models.ForeignKey(ProjectImage,on_delete=models.CASCADE)
    url = models.CharField(max_length=100)
    
    def __str__(self):
        return self.title