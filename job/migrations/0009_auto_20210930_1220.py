# Generated by Django 3.2.6 on 2021-09-30 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0008_auto_20210928_1914'),
    ]

    operations = [
        migrations.AddField(
            model_name='designation',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='job.hospital_department'),
        ),
        migrations.AlterUniqueTogether(
            name='designation',
            unique_together=set(),
        ),
    ]