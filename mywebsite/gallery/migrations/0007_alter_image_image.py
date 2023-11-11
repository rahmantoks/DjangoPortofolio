# Generated by Django 4.2.6 on 2023-11-11 07:34

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0006_alter_image_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='JPEG', keep_meta=True, quality=-1, scale=None, size=[1000, 800], upload_to='gallery/'),
        ),
    ]
