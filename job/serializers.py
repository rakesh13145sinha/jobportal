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

class CategoryRelatedJobSerializers(serializers.ModelSerializer):
    class Meta:
        model=Category_Related_Job
        fields=("id","designation","Speciality","hosptial_name",
                "location","salary","experince","hr_contact","hospitail_image","monthly_or_anual")



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


class NewsArticalPostSerializers(serializers.ModelSerializer):
    class Meta:
        model=NewsArticalPost  
        exclude=['likes','bookmark']

class NewsArticalSerializers(serializers.ModelSerializer):
    class Meta:
        model=NewsArticalPost  
        exclude=['likes','bookmark',"status","created_date","update"]


class PollSerializers(serializers.ModelSerializer):
    class Meta:
        model=Poll  
        fields=['id','poll_user','title','option1','option2','option3','option4','poll_status']

class PollVoteSerializers(serializers.ModelSerializer):
    class Meta:
        model=Poll  
        fields=['id','title','option1','option2','option3','option4','poll_status']

class ComplaintSerializers(serializers.ModelSerializer):
    class Meta:
        model=Complaint
        exclude=['likes','bookmark']

class CaseSerializers(serializers.ModelSerializer):
    class Meta:
        model=Complaint
        fields=["id","title","image","chief_complaint","complaint_status"]


class College_StorySerializers(serializers.ModelSerializer):
    class Meta:
        model=College_Story
        exclude=['likes','bookmark']

class ArticalsSerializers(serializers.ModelSerializer):
    class Meta:
        model=Articals
        exclude=['likes','bookmark']

class ArticalSerializers(serializers.ModelSerializer):
    class Meta:
        model=Articals
        exclude=['likes','bookmark',"status","created_date","update"]

class ResumeUploadSerializers(serializers.ModelSerializer):
    class Meta:
        model=ResumeUpload 
        fields="__all__"


class BannerSerializers(serializers.ModelSerializer):
    class Meta:
        model=HospitalBanner 
        fields="__all__"



class DesignationSerializers(serializers.ModelSerializer):
    class Meta:
        model=Designation
        fields=('id','position')


class HospitalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Hospital_Type
        fields='__all__'

