# Generated by Django 4.2.6 on 2023-11-04 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_post_lang'),
    ]

    operations = [
        migrations.RenameField(
            model_name='language',
            old_name='lang',
            new_name='language',
        ),
        migrations.RemoveField(
            model_name='category',
            name='subtitle',
        ),
        migrations.RemoveField(
            model_name='language',
            name='lang_id',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='subtitle',
        ),
        migrations.AddField(
            model_name='category',
            name='explanation',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='language',
            name='language_id',
            field=models.CharField(default='', max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tag',
            name='explanation',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='short',
            field=models.TextField(),
        ),
    ]
