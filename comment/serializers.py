from rest_framework import serializers
from .models import *
from job.models import Profile

class UserProfileSerializers(serializers.ModelSerializer):
	class Meta:
		model=Profile 
		fields=('id','profile_name','profileImage')

class AnswerSerializers(serializers.ModelSerializer):
	profile=UserProfileSerializers(read_only=True,many=False)
	class Meta:
		model=Answer
		fields=('id','comment','create','profile','like')
		
class QuestionSerializers(serializers.ModelSerializer):
	profile=UserProfileSerializers(read_only=True,many=False)
	class Meta:
		model=Question 
		fields=('id','question','create','profile','like')



			
