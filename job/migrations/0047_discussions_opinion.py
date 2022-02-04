# Generated by Django 3.2.6 on 2022-01-25 09:48

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('job', '0046_pollcomment_opinion'),
    ]

    operations = [
        migrations.AddField(
            model_name='discussions',
            name='opinion',
            field=models.ManyToManyField(related_name='agree_disagree', to=settings.AUTH_USER_MODEL),
        ),
    ]
