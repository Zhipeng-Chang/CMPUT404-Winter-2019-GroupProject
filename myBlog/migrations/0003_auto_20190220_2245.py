# Generated by Django 2.1.5 on 2019-02-21 05:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myBlog', '0002_auto_20190220_2241'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='host',
            field=models.URLField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='post',
            name='origin',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='url',
            field=models.URLField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]