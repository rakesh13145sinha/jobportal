
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
        exclude=['id']
       
class ProfileSerializers(serializers.ModelSerializer):
        
    class Meta:
        model=Profile
        exclude=['id']



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

class QuestionSerializers(serializers.ModelSerializer):
    
    
    class Meta:
        model=Question
        fields="__all__"
class AtteptQuestionSerializers(serializers.ModelSerializer):

    class Meta:
        model=AtteptQuestion
        fields="__all__"

class HospitalImgtourSerializers(serializers.ModelSerializer):
    
    class Meta:
        model=HospitalBanner
        fields="__all__"

class HospitalHighlightSerializers(serializers.ModelSerializer):
    
    class Meta:
        model=HospitalHighlight
        fields="__all__"

class HospitalSpecialitySerializers(serializers.ModelSerializer):
    
    class Meta:
        model=HospitalSpeciality
        fields="__all__"

class HospitalInfoSerializers(serializers.ModelSerializer):
    
    class Meta:
        model=HospitalInfo
        fields="__all__"