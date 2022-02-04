from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class Pages(models.Model):
    title=models.CharField(max_length=20)
    image=models.ImageField(upload_to="newspages/image")
    status=models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True,auto_now_add=False)

class NewsPages(models.Model):
    newspage=models.ForeignKey(Pages,on_delete=models.CASCADE)
    title=models.CharField(max_length=20)
    image=models.ImageField(upload_to="newspages/image")
    news=models.TextField()
    status=models.BooleanField(default=True)
    bookmark=models.ManyToManyField(User,related_name="newspage_bookmark")
    like=models.ManyToManyField(User,related_name="newspage_like")
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True,auto_now_add=False)

