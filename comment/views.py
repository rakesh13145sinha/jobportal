from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from .models import * 
from .serializers import * 
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status 
from django.contrib.auth.models import User


def get_profile(userid):	
	try:
		profile=Profile.objects.select_related('contact').get(contact__userdetail__id=userid)
		return profile 
	except Profile.DoesNotExist:
		raise Http404


 
class QuestionSubmit(APIView):
	
	def get(self,request,format=None):
		response={}
		
		username_id=request.GET.get('user_id')
		questionId=request.GET.get('question_id')
		get_profile(username_id)
		
		if questionId:
			try:
				que=Question.objects.prefetch_related('like').select_related('profile').get(id=questionId)
				serializer=QuestionSerializers(que,many=False).data
				
			
				serializer.update({"like":que.like.filter(id=username_id).exists()})
				serializer.update({"question_likes":que.like.count()})

				serializer1= AnswerSerializers(que.answer_set.all(),many=True).data
				serializer.update({"answer":serializer1})

				return Response(serializer,status=status.HTTP_200_OK)

			except Question.DoesNotExist:
				return Response({"message":"question id not found",'status':False},status=status.HTTP_404_NOT_FOUND)

		else:
			question=Question.objects.prefetch_related('like').select_related('profile').all().order_by('-create')
			for que in question:
				
				serializer=QuestionSerializers(que,many=False).data
				response[que.id]=serializer
				
				response[que.id].update({"like":que.like.filter(id=username_id).exists()})
				
				response[que.id].update({"question_likes":que.like.count()})

				serializer1= AnswerSerializers(que.answer_set.all(),many=True).data
				response[que.id].update({"answer":serializer1})

			return Response(response.values(),status=status.HTTP_200_OK)
		

	def post(self,request):
		username_id=request.GET.get('user_id')
		data=request.data
		question=Question.objects.create(profile=get_profile(username_id),question=data['question'])
		
		serializer=QuestionSerializers(question,many=False)
		return Response(serializer.data,status=status.HTTP_200_OK)

class AnswerSubmit(APIView):
	def post(self,request):
		username_id=request.GET.get('user_id')
		questiionId=request.GET.get('question_id')
		data=request.data
		Answer.objects.create(profile=get_profile(username_id),question=get_object_or_404(Question,id=questiionId),comment=data['comment'])
		return Response({"message":"replay posted","status":"true"},status=status.HTTP_200_OK)

class QuestionLike(APIView):
    def post(self,request):
        username_id=request.GET.get('user_id')
        question=Question.objects.prefetch_related('like').get(id=request.GET.get('qestion_id'))
        flag=question.like.filter(id=username_id).exists()
       
        if flag:
                question.like.remove(get_object_or_404(User,id=username_id))
                return Response({"like":"false"})
        else:
                question.like.add(get_object_or_404(User,id=username_id))
                return Response({"like":"true"})
        return Response({"message":"something issue"})

class AnswerLike(APIView):
    def post(self,request):
        username_id=request.GET.get('user_id')
        answer=Answer.objects.prefetch_related('like').get(id=request.GET.get('answer_id'))
        flag=answer.like.filter(id=username_id).exists()
        if flag:
                answer.like.remove(get_object_or_404(User,id=username_id))
                return Response({"like":"false"})
        else:
                answer.like.add(get_object_or_404(User,id=username_id))
                return Response({"like":"true"})
        return Response({"message":"something issue"})



