from functools import partial
from django.shortcuts import get_object_or_404
from rest_framework import response
from rest_framework.views import APIView 
from rest_framework.response import Response 
from django.contrib.auth import login,authenticate,logout
from rest_framework import status
from job.models import *
from job.serializers import *
from job.views import BookMark
from .serializers import *
from rest_framework.permissions import BasePermission, IsAuthenticated,IsAdminUser
from rest_framework.parsers import FileUploadParser
from django.contrib.auth.models import User

#permission_classes = [IsAuthenticated|ReadOnly]
#permission_classes = [IsAuthenticated]
##permission_classes = [AllowAny]
##permission_classes = [IsAdminUser]

# Create your views here.
class Admin_Login(APIView):
    def post(self,request):
       
        data=request.data 
        try:
            user=User.objects.get(email=data['email'])
        except Exception as msg:
            return Response({"message":str(msg)},status=status.HTTP_400_BAD_REQUEST)

        user=authenticate(request,username=user.username,password=data['password'])
        if user is not None:
            
            return Response({"status":True,"user_id":user.id,"username":user.username},status=status.HTTP_200_OK)
        else:
            return Response({"message":"something is wrong contact to developer"})

"""CATEGORY WITH HOW MANY IN  RELATED TO THIS CATEGORY JOB COUNT"""
class Job_Category_Post(APIView):
    #permission_classes = [IsAdminUser]
    def get(self,request):
        response={}
        categoryid=request.GET.get('category_id')
        if categoryid is not None:
            try:
                category=Job_By_Category.objects.get(id=categoryid)
            except Exception as msg:
                return Response({"message":str(msg)})
            serializers=Job_By_CategorySerializers(category,many=False).data 
            return Response(serializers,status=status.HTTP_200_OK)
        else:   
            categorys=Job_By_Category.objects.all()
            for category in categorys:
                serializers=Job_By_CategorySerializers(category,many=False).data 
                count_job_in_category=category.category_related_job_set.filter(job_status=True).count()
                serializers.update({"available_jobs":count_job_in_category})
                response[category.id]=serializers
            return Response(response.values(),status=status.HTTP_200_OK)


    parser_class = (FileUploadParser,)
    def post(self,request,*args, **kwargs):
        data=request.data 
        if not request.POST._mutable:
            request.POST._mutable = True
        serializer=Category(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=400)
        

    def put(self,request,format="json"):
        data=request.data 
        categoryId=request.GET.get('category_id')
        try:
            job_category=Job_By_Category.objects.get(id=categoryId)
        except Exception as e:
            return Response({"message":"Category id not exists","exceptions":str(e),"status":"False"},status=404)
        if data.get('image'):
            job_category.image.delete()
            job_category.image=data.get('image')
        serializers=Job_By_CategorySerializers(job_category,data=data,partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data,status=200)
        return Response(serializers.errors,status=404) 
   
    def delete(self,request):
        categoryId=request.GET.get('category_id')
        try:
            Job_By_Category.objects.get(id=categoryId).delete()
            return Response({"message":"category  deleted","status":True},status=200)
        except Exception as e:
            return Response({"message":"Category id not exists","exceptions":str(e)},status=404)


class JobCategorybyid(APIView):
    def get(self,request):
        categoryid=request.GET.get('category_id')
        jobid=request.GET.get('job_id')
        response={}
        if categoryid is not None:
            jobs=Category_Related_Job.objects.filter(category__id=categoryid,job_status=True).order_by('-created_date')
            for job in jobs:
                serializer=JobByCategorySerializers(job,many=False).data 
                serializer.update({"category":job.category.title})
                response[job.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        elif jobid is not None:
            try:
                job=Category_Related_Job.objects.get(id=jobid)
                serializer=Category_Related_JobSerializers(job,many=False)
                return Response(serializer.data,status=status.HTTP_200_OK)
            except Exception as msg:
                return Response({"message":"job id not found"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"job id not found"},status=status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        data=request.data 
        categoryid=request.GET.get('category_id') 
        if not request.POST._mutable:
            request.POST._mutable = True
        try:
            category=Job_By_Category.objects.get(id=categoryid)
            print("================",category.id)
        except Exception as msg:
            return Response({"message":"job id not found"},status=status.HTTP_400_BAD_REQUEST)
        data['category']=category.id
        print(data)
        serializer=JobByCategorySerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_200_OK)
    
    def put(self,request):
        jobid=request.GET.get('job_id') 
        data=request.data 
        if not request.POST._mutable:
            request.POST._mutable = True
        job=Category_Related_Job.objects.get(id=jobid)
        data['category']=job.category.id
        print(data)
        serializer=JobByCategorySerializers(job,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"job updated"},status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_200_OK)
    
    def patch(self,request):
        jobid=request.GET.get('job_id') 
        data=request.data 
        if not request.POST._mutable:
            request.POST._mutable = True
        job=Category_Related_Job.objects.get(id=jobid)
        data['category']=job.category.id
        print(data)
        if data['resion']:
            job.job_status=False
            job.resion=data['resion']
            job.save()
            return Response({"message":"job updated"},status=status.HTTP_200_OK)
           
        else:
            return Response({"message":"something is issue"},status=status.HTTP_200_OK)

"""API FOR DELETE JOBS MENS WHICH JOBS STATUS IS FALSE """       

class DeletedJobs(APIView):
    def get(self,request):
        category=Category_Related_Job.objects.filter(job_status=False).order_by("-created_date")
        serializers=Category_Related_JobSerializers(category,many=True) 
        return Response(serializers.data,status=status.HTTP_200_OK)
    
    def delete(self,request):
        jobid=request.GET.get('job_id') 
        job=Category_Related_Job.objects.get(id=jobid)
        job.job_status=True
        job.resion=""
        job.save()
        return Response({"message":"job retrive successful","status":True},status=status.HTTP_200_OK)



"""GET PAGE CATEGORY AND PAGE RELATED NEWS POSTED BY SUPER USER ONLY HERE GET METHOD  """
class Page(APIView):
    def get(self,request):
        pageid=request.GET.get('page_id')
        userid=request.GET.get('user_id')
        response={}
        if pageid is not None and userid is None:
            page=get_object_or_404(Pages,id=pageid)
            
            pagenews=page.newspages_set.all()
            for news in pagenews:
                newserializer=NewsPagesSerializers(news,many=False).data
                response[news.id]=newserializer
            return Response(response.values(),status=status.HTTP_200_OK)
        
        elif pageid is not None and userid is not None:
            page=get_object_or_404(Pages,id=pageid)
            user=get_object_or_404(User,id=userid)
            pagenews=page.newspages_set.all()
            for news in pagenews:
                newserializer=NewsPagesSerializers(news,many=False).data
                response[news.id]=newserializer
                response[news.id].update({
                    "like_status":news.like.filter(id=user.id).exists(),
                    "bookmark_status":news.bookmark.filter(id=user.id).exists()
                })
                

            return Response(response.values(),status=status.HTTP_200_OK)

        else:
            serializers=PagesSerializers(Pages.objects.all(),many=True).data
            return Response(serializers,status=status.HTTP_200_OK)

    def post(self,request):
        data=request.data 
        serializers=PagesSerializers(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data,status=status.HTTP_200_OK)
        else:
            return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
            
    def put(Self,request):
        data=request.data
        pageid=request.GET.get('page_id')
       
        serializers=PagesSerializers(get_object_or_404(Pages,id=pageid),data=data,partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data,status=status.HTTP_200_OK)
        else:
            return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)


 
    def delete(self,request):
        pageid=request.GET.get('page_id')
        get_object_or_404(Pages,id=pageid).delete()
        return Response({"message":"this news channel deleted"})

"""Page related news post"""
class NewsPagePost(APIView):
   
    def get(self,request):
        pagenewsid=request.GET.get('pagenews_id')
        if pagenewsid is not None :
            pagenews=NewsPages.objects.get(id=pagenewsid)
            serializers=NewsPagesSerializers(pagenews,many=False).data
        else:
            serializers=NewsPagesSerializers(NewsPages.objects.all(),many=True).data
        return Response(serializers,status=status.HTTP_200_OK)


    def post(self,request):
        page=request.GET.get('page_id')
        data=request.data 
        try:
            get_page=Pages.objects.get(id=page)
        except Exception as msg:
            return Response({"message":str(msg)})

        data['newspage']=get_page.id
        serializers=NewsPagesSerializers(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data,status=status.HTTP_200_OK)
        else:
            return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)

class PageNewsBookmark(APIView):
    def get(self,request):
        pageNews=request.GET.get('pagenews_id')
        userid=request.GET.get('user_id')
        user=get_object_or_404(User,id=userid)
        if userid is not None and pageNews is not None:
            try:
                pagenews=NewsPages.objects.get(id=pageNews)
            except Exception as e:
                return Response({"message":"complaint id not found","status":"false","exception":str(e)},status=400)
            try:
                if pagenews.bookmark.get(id=user.id):
                    pagenews.bookmark.remove(user)
                    return Response({"bookmark_status":"false"},status=200)
            except Exception as e:
                pagenews.bookmark.add(user)
                return Response({"bookmark_status":"true"},status=200)

        else:
            return Response({"message":"something is issue","status":False},status=status.HTTP_404_NOT_FOUND)


class PageNewsLike(APIView):
    def get(self,request):
        pageNews=request.GET.get('pagenews_id')
        userid=request.GET.get('user_id')
        user=get_object_or_404(User,id=userid)
        if userid is not None and pageNews is not None:
            try:
                pagenews=NewsPages.objects.get(id=pageNews)
            except Exception as e:
                return Response({"message":"pagenews id not found","status":False,"exception":str(e)},status=400)
            try:
                if pagenews.like.get(id=user.id):
                    pagenews.like.remove(user)
                    return Response({"news_like_status":"false"},status=200)
            except Exception as e:
                pagenews.like.add(user)
                return Response({"news_like_status":"true"},status=200)

        else:
            return Response({"message":"something is issue","status":False},status=status.HTTP_404_NOT_FOUND)


"""GET SPECIALITY AND DEPARTMENT  AND MORE INFO SPECIALITY AND DEPARTMENT BOTH ARE SAME"""      

class Speciality_And_Department(APIView):
    def get(self,request):
        spec_department=request.GET.get('department')
        response={}
        H_and_D=Hospital_Department.objects.all()
        if spec_department is not None:
            try:
                department=H_and_D.get(department_name=spec_department)
            except Exception as msg:
                return Response({"message":"department not found","status":False},status=status.HTTP_404_NOT_FOUND)
            jobs=Category_Related_Job.objects.filter(Speciality=department.department_name,job_status=True).order_by('-created_date')
            serializers=Category_Related_JobSerializers(jobs,many=True)
            return Response(serializers.data,status=status.HTTP_200_OK)
        else:
            for hd in H_and_D:
                jobs=Category_Related_Job.objects.filter(Speciality=hd.department_name,job_status=True)
                response[hd.id]={
                    "department":hd.department_name,
                    "total_job":jobs.count()
                }
            return Response(response.values())
    


"""SHOW PROFILE """
class UserProfile(APIView):
    def get(self,request):

        userid=request.GET.get('user_id')
        if userid is not None:
            register_user= Identification.objects.get(userdetail__id=userid)
            serializers=IdentificationSerializers(register_user,many=False).data
            serializers.update({
                "username":register_user.userdetail.username,
                "email":register_user.userdetail.email,
                "bookmark":Category_Related_Job.objects.filter(bookmark=register_user.userdetail).count(),
                
            })
            
        else:
            register_user= Identification.objects.filter(userdetail__is_superuser=False,userdetail__is_staff=False)
            serializers=IdentificationSerializers(register_user,many=True).data
        return Response(serializers,status=status.HTTP_200_OK)

    def delete(self,request):
        userid=request.GET.get('user_id')
        register_user= get_object_or_404(User,id=userid)
        register_user.delete()
        return Response({"message":"user id deleted successful","status":True},status=status.HTTP_200_OK)

"""SHOW ALL STATE"""
class Show_State(APIView):
    def get(self,request):
        state=request.GET.get('state')
        
        states=State.objects.all()
        
        response={}
        if state is not None:
            try:
                get_state=states.get(name=state)
            except Exception as msg:
                return Response({"message":"this state is not exists","status":False},status=404)
            jobs=Category_Related_Job.objects.filter(state=get_state.name,job_status=True).order_by('-created_date')
            serializers=Category_Related_JobSerializers(jobs,many=True)
            return Response(serializers.data,status=status.HTTP_200_OK)

        for state in states:
            jobs=Category_Related_Job.objects.filter(state=state,job_status=True).order_by('-created_date')
            response[state.id]={
                "name":state.name,
                "total_job":jobs.count()
            }
        return Response(response.values(),status=status.HTTP_200_OK)



"""THIS API FOR GET TOTAL JOBS """
class Total_Active_Jobs(APIView):
    def get(self,request):
        total_jobs=Category_Related_Job.objects.filter(job_status=True).order_by("-created_date")
        serializers=JobSerializers(total_jobs,many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)


class Add_Spec_Department(APIView):
   
    def post(self,request):
        data=request.data
        Hospital_Department.objects.get_or_create(department_name=data['department_name'])
        
        return Response({"message":"Specility or Department added successfull","status":True},status=200)
    
    def put(self,request):
        data=request.data
        departmentid=request.GET.get('department_name')
        try:
            hdepartment=get_object_or_404(Hospital_Department,department_name=departmentid)
            serializer=Hospital_DepartmentSerializers(hdepartment,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"hospital department updated successfull","status":True},status=200)
            else:
                return Response (serializers.errors,status=404)
            
        except Exception as msg:
            return Response({"messaage":"department id not found","status":False},status=404)
       

    def delete(self,request):
        departmentid=request.GET.get('department_name')
        try:
            get_object_or_404(Hospital_Department,department_name=departmentid).delete()
            return Response({"messaage":"department delete successful","status":True},status=200)
        except Exception as msg:
            return Response({"messaage":"department name not found","status":False},status=404)


    
class Add_Qualification(APIView):
   
    def post(self,request):
        data=request.data
        serializers=HigherQualificationSerializers(data=data)
        if serializers .is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors,status=404)
    
    def put(self,request):
        qualificationid=request.GET.get('qualification')
        data=request.data
        HQ=HigherQualification.objects.get(qualification=qualificationid)
        serializers=HigherQualificationSerializers(HQ,data=data,partial=True)
        if serializers .is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors,status=404)
    
    def delete(self,request):
        qualificationid=request.GET.get('qualification')
        try:
            HQ=HigherQualification.objects.get(qualification=qualificationid).delete()
        
            return Response({"message":"qualification deleted"},status=200)
        except Exception as msg:
            return Response({"message":"qualification not found"},status=404)


class Add_Designation(APIView):
   
    def post(self,request):
        data=request.data
        serializers=DesignationSerializers(data=data)
        if serializers .is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors,status=404)
    
    def put(self,request):
        position_name=request.GET.get('position')
        data=request.data
        pos=Designation.objects.get(position=position_name)
        serializers=DesignationSerializers(pos,data=data,partial=True)
        if serializers .is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors,status=404)
    
    def delete(self,request):
        position_name=request.GET.get('position')
        try:
            Designation.objects.get(position=position_name).delete()
        
            return Response({"message":"Designation deleted"},status=200)
        except Exception as msg:
            return Response({"message":"Designation not found"},status=404)



class Add_Hospital_Type(APIView):
    def get(self,request):
        HQ=Hospital_Type.objects.all()
        serializers=HospitalTypeSerializer(HQ,many=True)
        return Response(serializers.data)
   
    def post(self,request):
        data=request.data
        serializers=HospitalTypeSerializer(data=data)
        if serializers .is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors,status=404)
    
    def put(self,request):
        qualificationid=request.GET.get('hospitaltype_id')
        data=request.data
        HQ=Hospital_Type.objects.get(id=qualificationid)
        serializers=HospitalTypeSerializer(HQ,data=data,partial=True)
        if serializers .is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors,status=404)
    
    def delete(self,request):
        hospitaltypeid=request.GET.get('hospitaltype_id')
       
        HQ=Hospital_Type.objects.get(id=hospitaltypeid).delete()
        
        return Response({"message":"hospital type deleted"},status=404)