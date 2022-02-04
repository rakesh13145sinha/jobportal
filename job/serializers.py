from django.db.models import fields
from rest_framework import serializers 
from .models import *
from django.contrib.auth.models import User

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','username','email')

class IdentificationSerializers(serializers.ModelSerializer):
    
    class Meta:
        model=Identification
        fields='__all__'

class ProfileSerializers(serializers.ModelSerializer):
    # def validate(self,*args,**kwargs):
    #     print(self.contact)
        
    class Meta:
        model=Profile
        exclude=('follow','updated_date')

class ExperienceSerializers(serializers.ModelSerializer):
    class Meta:
        model=Experience
        fields='__all__'



class Job_By_CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model=Job_By_Category
        fields="__all__"

class Category_Related_JobSerializers(serializers.ModelSerializer):
    class Meta:
        model=Category_Related_Job
        
        exclude=('likes','bookmark','applicant','category')

class SubjectSerializers(serializers.ModelSerializer):
    class Meta:
        model=Subject
        fields='__all__'



class HigherQualificationSerializers(serializers.ModelSerializer):
    class Meta:
        model=HigherQualification
        fields=['id','qualification']

class StateSerializers(serializers.ModelSerializer):
    class Meta:
        model=State
        fields=['id','name']


class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model=Category 
        fields=('id','news_title')

class NewsArticalSerializers(serializers.ModelSerializer):

    class Meta:

        model=NewsArtical

        fields='__all__'

class Custome_JobSerializers(serializers.ModelSerializer):

    class Meta:

        model=Custome_Job 

        fields='__all__'
class NewsArticalPostSerializers(serializers.ModelSerializer):
    class Meta:
        model=NewsArticalPost  
        exclude=['likes','bookmark']


class PollSerializers(serializers.ModelSerializer):
    class Meta:
        model=Poll  
        fields=['id','poll_user','poll_title','option1','option2','option3','option4','poll_status','created_date','update']

class ComplaintSerializers(serializers.ModelSerializer):
    class Meta:
        model=Complaint
        exclude=['likes','bookmark']

class College_StorySerializers(serializers.ModelSerializer):
    class Meta:
        model=College_Story
        exclude=['likes','bookmark']

class ArticalsSerializers(serializers.ModelSerializer):
    class Meta:
        model=Articals
        exclude=['likes','bookmark']

class RequestJobPostSerializers(serializers.ModelSerializer):
    class Meta:
        model=RequestJobPost 
        fields="__all__"

class ResumeUploadSerializers(serializers.ModelSerializer):
    class Meta:
        model=ResumeUpload 
        fields="__all__"


class BannerSerializers(serializers.ModelSerializer):
    class Meta:
        model=Banner 
        fields="__all__"

class HomeBannerSerializers(serializers.ModelSerializer):
    class Meta:
        model=HomeBanner 
        fields="__all__"


class DesignationSerializers(serializers.ModelSerializer):
    class Meta:
        model=Designation
        fields=('id','position')


class HospitalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Hospital_Type
        fields='__all__'

class RecentSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model=RecentSearch
        exclude=["user"]