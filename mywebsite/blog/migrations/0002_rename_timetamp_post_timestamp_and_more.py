# Generated by Django 4.2.6 on 2023-10-31 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='timetamp',
            new_name='timestamp',
        ),
        migrations.RemoveField(
            model_name='category',
            name='thumbnail',
        ),
        migrations.RemoveField(
            model_name='post',
            name='thumbnail',
        ),
    ]
