from django.db import models
from django_resized import ResizedImageField

# Create your models here.

class ImageTag(models.Model):
    title = models.CharField(max_length=20)
    explanation = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Image(models.Model):
    caption = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    image = ResizedImageField(size=[1920, 1080], force_format='JPEG', upload_to="gallery/")
    upload_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(ImageTag)
    
    def __str__(self):
        return self.caption