# Generated by Django 3.2.6 on 2022-01-04 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0033_job_by_category_category_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='identification',
            name='current_job_location',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='identification',
            name='designation',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='identification',
            name='hightest_qualification',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='identification',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='identification',
            name='gender',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='identification',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='identification',
            name='status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='profile',
            unique_together=set(),
        ),
    ]
