
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


class Question(models.Model):
    EXAM= [
        ('PG-NEET', 'PG-NEET'),
        ('SS-NEET', 'SS-NEET'),
        
    ]
    exam=models.CharField(max_length=100,choices=EXAM)
    ProfileImage=models.ImageField(upload_to="question",null=True,blank=True)
    question=models.CharField(max_length=500,null=True)
    subject=models.CharField(max_length=100,null=True)
    option1=models.CharField(max_length=200,null=True)
    option2=models.CharField(max_length=200,null=True)
    option3=models.CharField(max_length=200,null=True)
    option4=models.CharField(max_length=200,null=True)
    correct_answer=models.CharField(max_length=20,null=True)
    detail=models.CharField(max_length=1000,null=True)

    status=models.BooleanField(default=False) 
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    update=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)

class AtteptQuestion(models.Model):
    SelectedOption= [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'D'),
        ('D', 'D')
        
        ]
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    selected_option=models.CharField(max_length=20,choices=SelectedOption)
    answer_status=models.BooleanField(default=False)

