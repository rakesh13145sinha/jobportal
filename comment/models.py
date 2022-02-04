from django.db import models
# Create your models here.
from job.models import Profile
from django.contrib.auth.models import User

class Question(models.Model):
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE)
    question=models.TextField()
    create=models.DateTimeField(auto_now=False,auto_now_add=True)
    #like=models.ManyToManyField(Profile,related_name="question_likes")
    like=models.ManyToManyField(User,related_name="question_likes")
    def __str__(self):
        return self.profile.profile_name

class Answer(models.Model):
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE)
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    comment=models.TextField()
    create=models.DateTimeField(auto_now=False,auto_now_add=True)
    #like=models.ManyToManyField(Profile,related_name="answer_like")
    like=models.ManyToManyField(User,related_name="answer_likes")
    def __str__(self):
        return "%s" %(self.profile.profile_name)

    # def __str__(self):
    #     return "%s (%s)" % (self.id,", ".join(user.username for user in self.like.all()),           
            
    #     )

"""This table for reply on comment """
class AnswerReply(models.Model):
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE)
    comment=models.ForeignKey(Answer,on_delete=models.CASCADE)
    reply=models.TextField()
    create=models.DateTimeField(auto_now=False,auto_now_add=True)
    like=models.ManyToManyField(Profile,related_name="reply_on_comment")

    def __str__(self):
        return self.profile.profile_name


