# Generated by Django 3.2.6 on 2021-10-07 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0022_skills'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='skill',
            field=models.TextField(null=True),
        ),
    ]