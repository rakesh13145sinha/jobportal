from rest_framework import serializers
from college.models import * 

class MedicalCollegeSerializers(serializers.ModelSerializer):
	class Meta:
		model=MedicalCollege  
		exclude=['entrance_exam','available_course']

class ExaminationSerializers(serializers.ModelSerializer):
	class Meta:
		model=Examination
		fields=['id','name']

class CourseSerializers(serializers.ModelSerializer):
	class Meta:
		model=Course
		fields=['name']