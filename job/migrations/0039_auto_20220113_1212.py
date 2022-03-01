# Generated by Django 3.2.6 on 2022-01-13 12:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('job', '0038_rename_abount_job_by_category_about'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='designation',
            name='department',
        ),
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='job.state'),
        ),
        migrations.AddField(
            model_name='identification',
            name='speciality',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='hospital_city_name',
            field=models.CharField(db_column='city', max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='identification',
            unique_together={('phone_number', 'userdetail')},
        ),
        migrations.AlterUniqueTogether(
            name='profile',
            unique_together={('contact',)},
        ),
        migrations.RemoveField(
            model_name='identification',
            name='designation',
        ),
    ]