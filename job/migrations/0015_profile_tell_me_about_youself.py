# Generated by Django 3.2.6 on 2021-10-04 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0014_rename_department_profile_degrees'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='tell_me_about_youself',
            field=models.TextField(null=True),
        ),
    ]
