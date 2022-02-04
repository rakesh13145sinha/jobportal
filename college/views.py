from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import * 
from .serializers import * 
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status 

class AllCollege(APIView):
	def get(self,request):
		college_id=request.GET.get('collegeid')

		response={}
		if college_id:
			try:
				info=MedicalCollege.objects.prefetch_related('available_course','entrance_exam').get(id=college_id)
			except ObjectDoesNotExist:
				return Response({"message":"college id not found","status":"false"},status=status.HTTP_400_BAD_REQUEST)
			serializers=MedicalCollegeSerializers(info,many=False).data
			Examination=[ExaminationSerializers(exam,many=False).data  for exam in info.entrance_exam.all()]
			course=[CourseSerializers(c,many=False).data  for c in info.available_course.all()]
			serializers.update({"Examination":Examination})
			serializers.update({"Course":course})
			return Response(serializers,status=200)
			
		full_info_college=MedicalCollege.objects.prefetch_related('available_course','entrance_exam').all()


		for info in full_info_college:
			serializers=MedicalCollegeSerializers(info,many=False).data
			Examination=[ExaminationSerializers(exam,many=False).data  for exam in info.entrance_exam.all()]
			course=[CourseSerializers(c,many=False).data  for c in info.available_course.all()]
			
			response[info.id]=serializers
			response[info.id].update({"Examination":Examination})
			response[info.id].update({"Course":course})
			

		return Response(response.values())

	def post(self,request):
		data=request.data 
		serializers=MedicalCollegeSerializers(data)
		if serializers.is_valid():
			serializers.save()
			return Response(serializers.data,status=status.HTTP_200_OK)
		return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
		
	def delete(self,request):
		collegeid=request.GET.get('college_id')
		get_object_or_404(MedicalCollege,id=collegeid).delete()
		return Response({"message":"college id deleted"},status=status.HTTP_200_OK)



class EnteranceExam(APIView):
	def get(self,reqest):
		serializers=ExaminationSerializers(Examination.objects.all(),many=True).data
		return Response(serializers)
	
	def post(self,request):
		data=request.data 
		serializers=ExaminationSerializers(data=data)
		if serializers.is_valid():
			serializers.save()
			return Response(serializers.data,status=status.HTTP_200_OK)
		return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
	
	def delete(self,request):
		collegeid=request.GET.get('exam_id')
		get_object_or_404(Examination,id=collegeid).delete()
		return Response({"message":"EnteranceExam id deleted"},status=status.HTTP_200_OK)

