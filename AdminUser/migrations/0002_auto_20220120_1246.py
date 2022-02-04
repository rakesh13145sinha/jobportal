# Generated by Django 3.2.6 on 2022-01-20 12:46

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('AdminUser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspages',
            name='bookmark',
            field=models.ManyToManyField(related_name='newspage_bookmark', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='newspages',
            name='like',
            field=models.ManyToManyField(related_name='newspage_like', to=settings.AUTH_USER_MODEL),
        ),
    ]
