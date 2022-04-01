from django.shortcuts import get_object_or_404
from rest_framework import response
from rest_framework.views import APIView 
from rest_framework.response import Response 
from django.contrib.auth import login,authenticate,logout
from rest_framework import status
from job.models import *
from job.serializers import *
from django.db.models import Q
from .serializers import *
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.parsers import FileUploadParser
from django.contrib.auth.models import User


def userdetails(user):
    user=get_object_or_404(User,id=user)   
    userdata={
        "bookmark":Category_Related_Job.objects.filter(bookmark=user).count(),
        "likes":Category_Related_Job.objects.filter(likes=user).count(),
        "appliedjobs":Category_Related_Job.objects.filter(applicant=user).count(),
        "savejobs":Category_Related_Job.objects.filter(bookmark=user).count(),
        "poll":user.poll_set.all().count(),
        "artical":user.articals_set.all().count(),
        "case":user.complaint_set.all().count(),
        "news":user.newsarticalpost_set.all().count(),
        #"follow":Profile.objects.filter(follow=user.id).count(),
        "following":Profile.objects.filter(follow=user.id).count()

        }
    return userdata


# Create your views here.
class Admin_Login(APIView):
    def post(self,request):
       
        data=request.data 
        try:
            user=User.objects.get(email=data['email'])
        except Exception as msg:
            return Response({"message":str(msg),"errors":"Invalid Email","status":False},status=status.HTTP_400_BAD_REQUEST)

        user=authenticate(username=user.username,password=data['password'])

        if user is not None:
            if user.is_superuser:
                try:
                    gettoken=Token.objects.get(user=user)
                except Exception as e:
                    return Response({"errors":str(e),"status":False},status=status.HTTP_401_UNAUTHORIZED)

            
                return Response({"status":True,
                                "user_id":user.id,
                                "username":user.username,
                                "superuser_status":user.is_superuser,
                                "token":gettoken.key},status=status.HTTP_200_OK)
            else:
                return Response({"status":True,"user_id":user.id,"username":user.username,"superuser_status":user.is_superuser},status=status.HTTP_200_OK)
        else:
            return Response({"errors":"Invalid Password ","status":False},status=status.HTTP_401_UNAUTHORIZED)





"""SHOW PROFILE """
class UserProfile(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes=[TokenAuthentication]
    def get(self,request):
        response={}
        userid=request.GET.get('user_id')
        if userid is not None:
            user=get_object_or_404(User,id=userid)
            serializer=UserSerializers(user,many=False).data
          
            register_user= Identification.objects.get(userdetail=user)
            serializers=IdentificationSerializers(register_user,many=False).data
            serializer.update(serializers)
           

            try:
                profile=Profile.objects.get(contact__userdetail__id=register_user.userdetail.id)
                profiles=ProfileSerializers(profile,many=False).data
                profiles['follow']=profile.follow.count()
                profiles['profile']=True
                serializer.update(profiles)
            except Exception as e:
                serializer.update({"profile":None})
           
            serializer.update(userdetails(user.id))
            return Response(serializer,status=status.HTTP_200_OK)
            
        else:
            
            users=User.objects.filter(is_superuser=False,is_staff=False).order_by('-id')
            for user in users:
                         
                register_user= Identification.objects.get(userdetail=user)

                serializers=IdentificationSerializers(register_user,many=False).data
                
                try:
                    profile=Profile.objects.get(contact__userdetail__id=register_user.userdetail.id)
                    serializers['image']=profile.profileImage.url if profile.profileImage  else None
                    serializers['profile']=True if profile else False
                    
                except Exception as e:
                    pass
                    #return Response({"message":str(e)})
                    
                    
            
                    
                    
                serializers["appliedjobs"]=Category_Related_Job.objects.filter(applicant=user).count()
                response[user.id]=serializers
                
        return Response(response.values(),status=status.HTTP_200_OK)

    def delete(self,request):
        userid=request.GET.get('user_id')
        register_user= get_object_or_404(User,id=userid)
        try:
            phone=Identification.objects.get(userdetail=register_user)
            SaveOtp.objects.get(phone_number=phone.phone_number).delete()
        except Exception as e:
            pass
        
        register_user.delete()
        return Response({"message":"User removed successful","status":True},status=status.HTTP_200_OK)




"""CATEGORY WITH HOW MANY IN  RELATED TO THIS CATEGORY JOB COUNT"""
class Job_Category_Post(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes=[TokenAuthentication]
    def get(self,request):
        response={}
        categoryid=request.GET.get('category_id')
        if categoryid is not None:
            try:
                category=Job_By_Category.objects.get(Q(id=categoryid) | Q(title=categoryid))
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
            job_category=Job_By_Category.objects.get(Q(id=categoryId) | Q(title=categoryId))
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
    permission_classes = [IsAdminUser]
    authentication_classes=[TokenAuthentication]
    def get(self,request):
        categoryid=request.GET.get('category_id')
        jobid=request.GET.get('job_id')
        designation=request.GET.get('designation')
        qualification=request.GET.get('qualification')
        state=request.GET.get('state')
        city=request.GET.get('city')
        response={}
        # query=Q(job_status=True)
        
        if categoryid is not None:
            query=Q( Q(job_status=True ) & Q(category__id=categoryid))
        
        elif jobid is not None:
            query=Q( Q(job_status=True ) & Q(id=jobid))
        
        elif designation is not None:
            query=Q( Q(job_status=True ) & Q(designation=designation))
        
        elif qualification is not None:
            
            query=Q( Q(job_status=True ) & Q(qualification__contains=qualification))
        elif state is not None:
            query=Q( Q(job_status=True ) & Q(state=state) )
        
        elif city is not None:
            query=Q( Q(job_status=True ) & Q(city=city))
       
        else:
            query=Q(job_status=True)
        
        jobs=Category_Related_Job.objects.filter(query).order_by('-created_date')
        for job in jobs:
            
            serializer=JobSerializers(job,many=False).data
            serializer['bookmark']=job.bookmark.all().count()
            serializer['likes']=job.likes.all().count()
            serializer['applicant']=job.applicant.all().count()
            serializer["category"]=job.category.title
            if jobid is not None:
                return Response(serializer,status=status.HTTP_200_OK)
            response[job.id]=serializer
        return Response(response.values(),status=status.HTTP_200_OK)
        

            

    def post(self,request):
        data=request.data 
        categoryid=request.GET.get('category_id') 
        
        if not request.POST._mutable:
            request.POST._mutable = True
        try:
            if categoryid.isdigit():
                Query=Q(id=categoryid)
                print("if part")
            else:
                Query=Q(title=categoryid)
                print("elsepart")
            category=Job_By_Category.objects.get(Query )
            print("================",category.id)
        except Exception as msg:
            
            return Response({"message":"job id not found"},status=status.HTTP_400_BAD_REQUEST)
        data['category']=category.id
        
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
       
        if data['resion']:
            job.job_status=False
            job.resion=data['resion']
            job.save()
            return Response({"message":"job updated"},status=status.HTTP_200_OK)
           
        else:
            return Response({"message":"something is issue"},status=status.HTTP_200_OK)

"""API FOR DELETE JOBS MeaNS WHICH JOBS STATUS IS FALSE """       

class DeletedJobs(APIView):
    def get(self,request):
        jobid=request.GET.get('job_id')
        if jobid is not None:
            job=get_object_or_404( Category_Related_Job,id=jobid)
            job.job_status=True
            job.resion=""
            job.save()
            return Response({"message":"job retrive successful","status":True},status=status.HTTP_200_OK)
        else:
            category=Category_Related_Job.objects.filter(job_status=False).order_by("-created_date")
            serializers=Category_Related_JobSerializers(category,many=True) 
            return Response(serializers.data,status=status.HTTP_200_OK)
    
    
       
"""Applied jobs details"""
class AppliedJobDetail(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes=[TokenAuthentication]
    def get(self,request):
        response={}
        total_jobs=Category_Related_Job.objects.filter(applicant__isnull=False).order_by("-created_date")
        for job in total_jobs:

            serializers=JobSerializers(job,many=False).data
            
            serializers['bookmark']=job.bookmark.all().count()
            serializers['likes']=job.likes.all().count()
            serializers['applicant']=job.applicant.all().count()
            response[job.id]=serializers
        return Response(response.values(),status=status.HTTP_200_OK)

"""CASE API"""
class CaseData(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes=[TokenAuthentication]
    def get(self,request,*args,**kwargs):
        caseid=request.GET.get('case_id')
        if caseid is not None:
            query=Q(id=caseid)
        else:
            query=Q(complaint_status=True)
        response={}
        
        comp=Complaint.objects.filter(query).order_by('-created_date')
        if comp.exists()==False:
            return Response({"message":"complaint id not exists","status":False},status=status.HTTP_400_BAD_REQUEST)
        for case in comp:
            
            comment=case.discussions_set.count()
            serializers=ComplaintSerializers(case,many=False).data
            serializers['likes']=case.likes.all().count()
            serializers['bookmark']=case.bookmark.all().count()
            serializers['complaint_id']=case.complaint_id.username
            response[case.id]=serializers
            response[case.id].update({"comment":comment})
        
        return Response(response.values(),status=status.HTTP_200_OK)
    
"""POLL API"""
class PollView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes=[TokenAuthentication]
    def get(self, request, *args, **kwargs):
        pollid=request.GET.get('poll_id')
        response={}
        if pollid is not None:
            query=Q(id=pollid)
        else:
            query=Q(poll_status=True)
        polls=Poll.objects.select_related('poll_user').filter(query)
        for poll in polls:
            serializers=PollSerializers(poll,many=False).data
            serializers['poll_user']=poll.poll_user.username
            serializers['likes']=poll.likes.count()
            response[poll.id]=serializers
        return Response(response.values(),status=status.HTTP_200_OK)

"""ARTICAL  API"""
class ArticalView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes=[TokenAuthentication]
    def get(self, request, *args, **kwargs):
        articalid=request.GET.get('artical_id')
        response={}
        if articalid is not None:
            query=Q(id=articalid)
        else:
            query=Q(art_status=True)
        articals=Articals.objects.select_related('user').filter(query)
        for artical in articals:
            serializers=ArticalsSerializers (artical,many=False).data
            serializers['user']=artical.user.username
            serializers['likes']=artical.likes.count()
            response[artical.id]=serializers
        return Response(response.values(),status=status.HTTP_200_OK)
            

"""NEW ARTICAL VIEW API"""
class NewArticalView(APIView):
    
    permission_classes = [IsAdminUser]
    authentication_classes=[TokenAuthentication]
    def get(self, request, *args, **kwargs):
        articalnewsid=request.GET.get('articalnews_id')
        response={}
        if articalnewsid is not None:
            query=Q(id=articalnewsid)
        else:
            query=Q(artical_status=True)
        newsarticals=NewsArticalPost .objects.select_related('userid').filter(query).order_by('-id')
        for news in newsarticals:
            serializers=NewsArticalPostSerializers (news,many=False).data
            serializers['userid']=news.userid.username
            serializers['likes']=news.likes.count()
            response[news.id]=serializers
        return Response(response.values(),status=status.HTTP_200_OK)

        




"""GET SPECIALITY AND DEPARTMENT  AND MORE INFO SPECIALITY AND DEPARTMENT BOTH ARE SAME"""      

class Speciality_And_Department(APIView):
    def get(self,request):
        spec_department=request.GET.get('department')
        response={}
        
        if spec_department is not None:
            try:
                department=Hospital_Department.objects.get(department_name=spec_department)
            except Exception as msg:
                return Response({"message":"department not found","status":False},status=status.HTTP_404_NOT_FOUND)

            jobs=Category_Related_Job.objects.filter(Speciality=department.department_name,job_status=True).order_by('-created_date')
            serializers=Category_Related_JobSerializers(jobs,many=True)
            return Response(serializers.data,status=status.HTTP_200_OK)
        else:
            H_and_D=Hospital_Department.objects.all()
            for hd in H_and_D:
                jobs=Category_Related_Job.objects.filter(Speciality=hd.department_name,job_status=True)
                response[hd.id]={
                    "department":hd.department_name,
                    "total_job":jobs.count()
                }
            return Response(response.values())
    




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



"""NOT IN USER """
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


#NEW ADMIN PANNEL START HERE

class Dashboard(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes=[TokenAuthentication]
    def get(self,request,*args,**kwargs):
        
        return Response({
            "user":User.objects.filter(is_superuser=False).count(),
            "total_jobs":Category_Related_Job.objects.count(),
            "category":Job_By_Category.objects.count(),
            "appliedjobs":Category_Related_Job.objects.filter(applicant__isnull=False).count(),
            "savejobs":Category_Related_Job.objects.filter(bookmark__isnull=False).count(),
            "poll":Poll.objects.count(),
            "artical":Articals.objects.count(),
            "case":Complaint.objects.count(),
            "news":NewsArticalPost.objects.count()

        })


class QuestionPost(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes=[TokenAuthentication]
    def get(self,request):
        question=request.GET.get('id')
        examination=request.GET.get('exam')
        
        if question is not None:
            
            serializer=QuestionSerializers(Question.objects.get(id=question),many=False)
            return Response(serializer.data)
        
        elif examination is not None:
            serializer=QuestionSerializers(Question.objects.filter(exam__iexact=examination).order_by("-created_date"),many=True)
            return Response(serializer.data)

        elif examination is not None:
            serializer=QuestionSerializers(Question.objects.filter(subject__iexact=examination).order_by("-created_date"),many=True)
            return Response(serializer.data)
        
        else:
            serializer=QuestionSerializers(Question.objects.all().order_by("-created_date"),many=True)
            return Response(serializer.data)

    def post(self,request):
        data=request.data 
        
        serializer=QuestionSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def put(self,request):
        question=request.GET.get('id')
        exam=get_object_or_404(Question,id=question)
        data=request.data 
        serializer=QuestionSerializers(exam,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request):
        question=request.GET.get('id')
        get_object_or_404(Question,id=question).delete()
        return Response({"message":"question deleted","status":True},status=status.HTTP_200_OK)

"""HOSPITAL TOUR POST"""

class HospitlMultiimage(APIView):
   
    def get(self,request,id):
        
        response={}
        hospital=get_object_or_404(HospitalInfo,id=id)
        hospitalbanner=HospitalBanner.objects.filter(hospital=hospital)
        for banner in hospitalbanner:
            response[banner.id]={
                "id":banner.id,
                "hospitalid":id,
                "image":banner.file.url
                }
        return Response(response.values())

    # permission_classes = [IsAdminUser]
    # authentication_classes=[TokenAuthentication]
    def post(self,request,id):
        
        data=request.data
        hospital=get_object_or_404(HospitalInfo,id=id)
        data['hospital']=hospital.id
        serializer=HospitalImgtourSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
                
        
    
    def delete(self, request,id, *args, **kwargs):
        HospitalBanner.objects.get(id=id).delete()
        return Response({"message":"Job related hospital image deleted"})

class HospitalHighlights(APIView):
    # permission_classes = [IsAdminUser]
    # authentication_classes=[TokenAuthentication]
    def get(self,request,id):
        
        response={}
        hospital=get_object_or_404(HospitalInfo,id=id)
        highlight=HospitalHighlight.objects.filter(hospital=hospital)
        for h in highlight:
            response[h.id]={
                "id":h.id,
                "hospitalid":id,
                "title":h.title,
                "image":h.file.url
                }
        return Response(response.values())
    
    def post(self,request,id):
        data=request.data
        hospital=get_object_or_404(HospitalInfo,id=id)
        data['hospital']=hospital.id
        serializer=HospitalHighlightSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
                
        
    
    def delete(self, request,id, *args, **kwargs):
        HospitalHighlight.objects.get(id=id).delete()
        return Response({"message":"Job related hospital highlight deleted"})


class HospitalSpecialities(APIView):
    # permission_classes = [IsAdminUser]
    # authentication_classes=[TokenAuthentication]
    def get(self,request,id):
        
        response={}
        hospital=get_object_or_404(HospitalInfo,id=id)
        highlight=HospitalSpeciality.objects.filter(hospital=hospital)
        for h in highlight:
            response[h.id]={
                "id":h.id,
                "hospitalid":id,
                "title":h.title,
                "image":h.file.url
                }
        return Response(response.values())
    
    def post(self,request,id):
        data=request.data
        hospital=get_object_or_404(HospitalInfo,id=id)
        data['hospital']=hospital.id
        serializer=HospitalSpecialitySerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
                
        
    
    def delete(self, request,id, *args, **kwargs):
        HospitalSpeciality.objects.get(id=id).delete()
        return Response({"message":"Job related hospital highlight deleted"})


class HospitalInformations(APIView):
    # permission_classes = [IsAdminUser]
    # authentication_classes=[TokenAuthentication]
    def get(self,request):
        hospitalid=request.GET.get('hospitalid')
        hospitalname=request.GET.get('name')
        location=request.GET.get('location')
        
        if hospitalid is not None:
            highlight=HospitalInfo.objects.get(id=hospitalid)
            serializers=HospitalInfoSerializers(highlight,many=False)
            return Response(serializers.data)
        elif hospitalname is not None:
            highlight=HospitalInfo.objects.filter(name__startswith=hospitalname)
            serializers=HospitalInfoSerializers(highlight,many=True)
            return Response(serializers.data)
        elif hospitalname is not None and location is not None:
            highlight=HospitalInfo.objects.get(name__iexact=hospitalname,location__iexact=location)
            serializers=HospitalInfoSerializers(highlight,many=False)
            return Response(serializers.data)
        else:

            highlight=HospitalInfo.objects.all().order_by("-id")
            serializers=HospitalInfoSerializers(highlight,many=True)
            return Response(serializers.data)
    
    def post(self,request):
        data=request.data
        serializer=HospitalInfoSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
                
    def put(self,request):
        hospitalid=request.GET.get('hospitalid')
        data=request.data
        highlight=HospitalInfo.objects.get(id=hospitalid)
        serializer=HospitalInfoSerializers(highlight,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)   
    
    def delete(self, request, *args, **kwargs):
        HospitalInfo.objects.get(id=id).delete()
        return Response({"message":"Job related hospital highlight deleted"})



"""HOSPITAL OVER"""
class HospitalTypePost(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes=[TokenAuthentication]
    def post(self,request,hospitaltype):
        if not request.POST._mutable:
            request.POST._mutable = True
        Hospital_Type.objects.get_or_create(hospitaltype=hospitaltype)
        return Response({"message":"hospital_type posted successfull","status":True},status=status.HTTP_200_OK)
        
