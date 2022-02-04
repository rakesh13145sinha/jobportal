
from django.db.models import fields
from rest_framework import serializers
from job.models import *
from .models import *

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','username','email','first_name')

class IdentificationSerializers(serializers.ModelSerializer):
    
    class Meta:
        model=Identification
        fields='__all__'
        depth=3
# class ProfileSerializers(serializers.ModelSerializer):
        
#     class Meta:
#         model=Profile
#         fields=['profile_name','profileImage','status',
#                 'ug','ug_institute_name','pg','pg_institute_name',
#                 'current_institute','current_department','degrees',
#                 'tell_me_about_youself','current_job_location','skill'
#                 ]


class Category(serializers.ModelSerializer):
    class Meta:
        model=Job_By_Category
        fields=['title','image']

class JobByCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model=Category_Related_Job
        exclude=('likes','bookmark','applicant','resion','top_job')

class JobSerializers(serializers.ModelSerializer):
    class Meta:
        model=Category_Related_Job
        fields='__all__'

class PagesSerializers(serializers.ModelSerializer):
    class Meta:
        model=Pages
        fields='__all__'

class NewsPagesSerializers(serializers.ModelSerializer):
    class Meta:
        model=NewsPages
        exclude=('like','bookmark')
class Hospital_DepartmentSerializers(serializers.ModelSerializer):
    class Meta:
        model=Hospital_Department
        fields="__all__"

class DesignationSerializers(serializers.ModelSerializer):
    class Meta:
        model=Designation
        fields="__all__"