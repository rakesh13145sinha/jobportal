# Generated by Django 3.2.6 on 2021-10-04 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0013_experience'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='department',
            new_name='degrees',
        ),
    ]
