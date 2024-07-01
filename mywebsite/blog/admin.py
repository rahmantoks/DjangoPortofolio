from django.contrib import admin
from .models import Author, Category, Post, Tag, Language
from gallery.models import Image, ImageTag
from projects.models import Project, ProjectImage
from django_summernote.admin import SummernoteModelAdmin

class PostAdmin(SummernoteModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    summernote_fields = ('overview','short')

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Author)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Language)
admin.site.register(Image)
admin.site.register(ImageTag)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectImage)
