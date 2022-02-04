from django.http import response
from django.shortcuts import render,get_object_or_404
from rest_framework.response import Response 
from rest_framework.parsers import FormParser,MultiPartParser,JSONParser 
from rest_framework import status 
from .models import *
from .send_otp import *
from django.db.models import Q, query
from rest_framework.views import APIView
from django.core.exceptions import AppRegistryNotReady, ObjectDoesNotExist
from .serializers import *
from django.contrib.auth.models import User
import random
from django.contrib.auth import authenticate,login,logout
import ast
from django.db.models import Count
from datetime import *
import secrets
import string
import time
from comment.views import get_profile
import operator
from functools import partial, reduce
from rest_framework.parsers import FileUploadParser


"""REGISTRATION LOGIN LOGOUT AND RESEND OTP API START HERE"""

'''api/reg/phone/'''
'''only phone number'''

class UserRegistration(APIView):
     
    def post(self,request,*args,**kwargs):
        data=request.data
        generated_otp = random.randint(1000,9999)
        phone=data['phone_number']
        if len(phone)>10 or len(phone)<10:
        
            return Response({"message":"Phone number should 10 digit"},status=status.HTTP_406_NOT_ACCEPTABLE)
        
        elif phone.isdigit()==False:
            
            return Response({"message":"phone number should digit"},status=status.HTTP_406_NOT_ACCEPTABLE)
        
       

        try:
            get_otp_from_database=SaveOtp.objects.get(phone_number=phone)
            get_otp_status=True
        except Exception as msg:
            get_otp_status=False
            pass
        
        try:
            identification= Identification.objects.get(phone_number=phone)
            if data.get('email') is not None or data.get('profile_name') is not None:
                return Response({'message':"authorized user","status":identification.status},status=status.HTTP_200_OK)

            elif identification.status==True:
                if get_otp_status:
                    sending_otp(get_otp_from_database.otp,phone)
                else:
                    SaveOtp.objects.create(phone_number=phone,otp=generated_otp)
                    sending_otp(generated_otp,phone)
                return Response({ 'message':"Otp sented Successful","status":identification.status},status=status.HTTP_200_OK)
            else:
               
                sending_otp(get_otp_from_database.otp,phone)
                print("sec time otp")
                return Response({'message':"authorized user","status":identification.status},status=status.HTTP_200_OK)
        
        except Exception as msg:
           
            print("new user",generated_otp)
            random_generated_number=random.randint(10000,99999)
            
            try:
                user=User.objects.create_user(
                                            username=data['profile_name']+"@job"+str(random_generated_number),
                                            email=data['email'],
                                        )
            except Exception as msg:
                return Response({"message":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
            try:
                reg_pro=Identification.objects.create(
                                        userdetail=user,
                                            phone_number=phone,
                                            profile_name=data['profile_name'],
                                            current_job_location=data['current_job_location'],
                                            speciality=data['speciality'],
                                            hightest_qualification=data['hightest_qualification']

                                            )
                

            except Exception as msg:
                return Response({"message":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
            try:
                SaveOtp.objects.create(phone_number=phone,otp=generated_otp)
               
            except Exception as msg:
                return Response({"message":str(msg)})
            try:
                sending_otp(generated_otp,phone)
            except Exception as msg:
                return Response({"message":str(msg)})

            return Response({'message':"Otp sented Successful","registration":"registration complited","status":reg_pro.status},status=status.HTTP_200_OK)
        

"""VALIDATE OTP AUTHENTICATION AND LOGIN WITH OTP""" 
"""api/auth/otp"""
class Validate_OTP(APIView):
   

    def post(self,request) :
        data=request.data
        try:
           
            data['phone_number']
            data['otp']
            print(data['otp'])
        except Exception as msg:
            return Response({"message":str(msg),"status":False,"required_field":True})
        if len(data['phone_number'])>10 or len(data['phone_number'])<10:
        
            return Response({"message":"Phone number should 10 digit"},status=status.HTTP_406_NOT_ACCEPTABLE)
        
        elif data['phone_number'].isdigit()==False:
            
            return Response({"message":"phone number should digit"},status=status.HTTP_406_NOT_ACCEPTABLE)

        
        try:
            get_contact_number=Identification.objects.get(phone_number__iexact=data['phone_number'])
            
        except Exception as msg:
            return Response({"message":str(msg)})
               
        try:
            saved_otp_on_this_number=SaveOtp.objects.get(phone_number__iexact=data['phone_number'])
        except Exception as msg:
            return Response({"message":str(msg)})
        
        """OTP VARIFICATION """
        if data['otp']==saved_otp_on_this_number.otp:
              
            saved_otp_on_this_number.delete()

            get_contact_number.status=True

            get_contact_number.save()
            
            Profile.objects.get_or_create(contact=get_contact_number)
                

            serializer=IdentificationSerializers(get_contact_number,many=False).data
            serializer.update({
                    "user_id":get_contact_number.userdetail.id,
                    "email":get_contact_number.userdetail.email,
                    "username":get_contact_number.userdetail.username,
                    "profile_name":get_contact_number.profile_name
                    })

            return Response(serializer,status=status.HTTP_202_ACCEPTED)
            
        else:
            return Response({"message":"Enter wrong opt"},status=status.HTTP_404_NOT_FOUND)
        
    
class Resend_otp(APIView):
    
    def post(self, request):
        data =  request.data

        generated_otp = random.randint(1000,9999)

        try:
            get_otp_from_database=SaveOtp.objects.get(phone_number=data['phone_number'])
            get_otp_status=True
        except Exception as msg:
            SaveOtp.objects.create(phone_number=data['phone_number'],otp=generated_otp)
            get_otp_status=False
            pass
        
      
        if get_otp_status:
            sending_otp(get_otp_from_database.otp,data['phone_number'])
        else:
            sending_otp(generated_otp,data['phone_number'])

        try:
            contact=Identification.objects.get(phone_number=data['phone_number'])
        except Exception as msg:
            return Response({"message":"this phone is not a register try first registration","status":False},status=status.HTTP_400_BAD_REQUEST)
        return Response({'status':contact.status,'message':"Otp resent Successful"},status=status.HTTP_200_OK)
       



class Logout(APIView):

    def get(self,request,format="json"):
        logout(request)
        return Response({"message": "Successful Logout"},status=status.HTTP_200_OK)


#####################################ACCOUNT API FINISH##################
"""PERSONAL INFORMATION ABOUT LOGED USER"""

"""HERE UPDATE THE SOME BASE INFO ABOUT USER JUST LIKE GENDER LANGUAGE DATE OF BIRTH EMAIL ID """
"""user/personal/info"""
class UpdatePersonalInfo(APIView):
    def get(self,request):
        response={
            "gender":['Male','Female'],
            "language":['Hindi','English','Telgu']
        
        }
        return Response(response,status=200)

    def put(self,request,format=None):
        
        username_id=request.GET.get('user_id')

        """CHECK PASS KEY IS IF WRONG THEN GIVE ERROR MESSAGE"""
        if username_id is None:
            return Response({"message":"Enter wrong key check and try again"},status=404)

        """GETTING REQUESTED USER ID """
        user=get_object_or_404(User,id=username_id)

        
        """HERE ALL DATA COMMING FROM USER FOR UPDATE"""
        data=request.data
        """TRY UPDATE FOR EMAIL IF EMAIL IS COMMING FOR UPDATE"""
        if data.get('email'):
            user.email=data.get('email')
            user.save()
        """GETTING IDENTIFICATION"""
        contact=get_object_or_404(Identification, userdetail=user)
        
        
        
        serializers=IdentificationSerializers(contact,data=data,partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response({"message":"update successfull","status":"true"},status=201)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)

            

"""HERE PROFILE RELETED ALL DETAIL  AND PROFESSION RELATED DATA HERE  GET POST PUT  PATCH"""
"""api/job/profile"""
class User_Profile(APIView):
    def get(self,request,format=None):
        username_id=request.GET.get('user_id')
        shwo_profile=request.GET.get('requested_user_id')
        if username_id:
            userid=Q(id=username_id)
        elif shwo_profile:
            userid=Q(id=shwo_profile)
        user=get_object_or_404(User,userid)
        contact=user.identification_set.get(userdetail=user)
        profile=contact.profile_set.get(contact=contact)

        """getting all related news artical post by this user"""
        self_posted_NewArticals=user.newsarticalpost_set.all().count()
        

        """getting all related all case posted by this user"""
        self_posted_cases=user.complaint_set.all().count()
    
        """getting all related all college story posted count"""
        self_posted_college_story=user.college_story_set.all().count()
        
        
        """getting all related poll posted count"""
        self_posted_poll=user.poll_set.all().count()
        
        """getting all related artical post count"""

        self_posted_artical=user.articals_set.all().count()
        
        
        
        if username_id:
            status_data={
                "bookmark_status":Category_Related_Job.objects.filter(bookmark__id=user.id).count(),
                "jobs_like":Category_Related_Job.objects.filter(likes__id=user.id).count(),
                "follow":profile.follow.filter(id=user.id).count(),
                "following":Profile.objects.filter(follow=profile.contact.userdetail).count(),
                "applied_jobs":Category_Related_Job.objects.filter(applicant=user.id).count() ,

                
                "case_like":self_posted_cases+Complaint.objects.filter(bookmark=user).count()+Complaint.objects.filter(likes=user).count(),

                
                "news_post_like":self_posted_NewArticals+NewsArticalPost.objects.filter(bookmark=user).count()+NewsArticalPost.objects.filter(likes=user).count(),

            
                "artical_like":self_posted_artical+Articals.objects.filter(bookmark=user).count()+Articals.objects.filter(likes=user).count(),
            
                
                "college_story_likes":self_posted_college_story+College_Story.objects.filter(bookmark=user).count()+College_Story.objects.filter(likes=user).count(),

                
                "poll_likes":self_posted_poll+Poll.objects.filter(bookmark=user).count()+Poll.objects.filter(likes=user).count(),
                
                

                }
        elif shwo_profile:
            status_data={
                "follow":profile.follow.filter(id=user.id).count(),
                "following":Profile.objects.filter(follow=profile.contact.userdetail).count(),
                "applied_jobs":Category_Related_Job.objects.filter(applicant=user.id).count() ,
                "case_like":self_posted_cases,
                "news_post_like":self_posted_NewArticals,
                "artical_like":self_posted_artical,
                "college_story_likes":self_posted_college_story,
                "poll_likes":self_posted_poll,
                }
            
        
        serializer=UserSerializers(user,many=False).data
        serializer1=IdentificationSerializers(contact,many=False).data
        serializer2=ProfileSerializers(profile,many=False).data
        serializer2.update(serializer1)
        serializer2.update(serializer)
        serializer2.update(status_data)
        return Response(serializer2,status=200)
        
       
    def post(self,request):
        if not request.POST._mutable:
            request.POST._mutable = True 
        data = ast.literal_eval(request.data['registerdata'])
        print(data)
        print("======")
    
        data['profileImage']=request.FILES['profileImage']
        print(data)

        serializer=ProfileSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=400)
        
                                  
    def put(self,request,format=None):
        if not request.POST._mutable:
            request.POST._mutable = True 
        # data = ast.literal_eval(request.data['registerdata'])
        data=request.data
        print(data)
       
        usernameid=request.GET.get('user_id')
        user=get_object_or_404(User,id=usernameid)
        
        try:
            profile=Profile.objects.get(contact__userdetail=user)
        except Exception as e:
            return Response({"message":"profile  not exists","status":"false","exception":str(e)},status=400)
        
      

        #data['profileImage']=request.FILES['profileImage']
        print(data)
        serializer=ProfileSerializers(profile,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=404)
    
    def patch(self,request,format=None):
        data=request.data
        usernameid=request.GET.get('user_id')
        user=get_object_or_404(User,id=usernameid)
        try:
            profile=Profile.objects.select_related('contact').get(contact__userdetail=user)
        except Exception as e:
            return Response({"message":"profile  not exists","status":"false","exception":str(e)},status=400)
        
        if data.get('profile_name'):
            get_profile_name=Identification.objects.get(id=profile.contact.id)
            get_profile_name.profile_name=data.get('profile_name')
            get_profile_name.save()
        
        serializer=ProfileSerializers(profile,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"profile updated","status":True},status=200)
        else:
            return Response(serializer.errors,status=404)

"""GET PROFESSIONAL INFO"""
"""api/user/profession/info"""
class ProfessionalInfo(APIView):
    def get(self,request):
       
        list_of_ug_degree=['MBBS','BDS','BAMS','BUMS','BHMS','BYNS','B.V.Sc & AH']
        list_of_pg_degree=['Anaesthesiology','Biochemistry','Community Health','Dermatology',
                            'Family Medicine','Forensic Medicine','General Medicine','Microbiology','Paediatrics',
                            'Palliative Medicine','Pathology','Skin and Venereal diseases','Ear, Nose and Throat',
                            'General Surgery','Ophthalmology','Orthopaedics','Obstetrics and Gynaecology',
                            'Dermatology, Venerology and Leprosy'
                            ]
        ug_of_institute=['KIMS-Krishna Institute of Medical','Osmania Medical College',
                            'ESIC Medical College, Hyderabad',"Dr. Patnam Mahender Reddy",
                            'Mamata Academy of Medical','Government Medical College',
                            'Mahavir Institute of Medical Science','Surabhi Institute of Medical Science'
                            ]
        pg_of_institute=['GANDHI MEDICAL COLLEGE','Osmania Medical College',
                            'NIZAMS INSTITUTE OF MEDICAL SCIENCES',"KAKATIYA MEDICAL COLLEGE",
                            'DECCAN COLLEGE OF MEDICAL SCIENCES','KAMINENI INSTITUTE OF MEDICAL SCIENCES',
                            'SVS MEDICAL COLLEGE','MAMATA MEDICAL COLLEGE','MALLA REDDY INSTITUTE OF MEDICAL SCIENCES',
                            'BHASKAR MEDICAL COLLEGE','SHADAN INSTITUTE OF MEDICAL SCIENCES, RESEARCH CENTRE AND TEACHING HOSPITAL',
                            'MEDICITI INSTITUTE OF MEDICAL SCIENCES','MNR MEDICAL COLLEGE AND HOSPITAL','PRATHIMA INSTITUTE OF MEDICAL SCIENCES',
                            'CHALMEDA ANAND RAO INSTITUTE OF MEDICAL SCIENCES'
                            ]
       
        hightest_qualification=[ qual.qualification for qual in HigherQualification.objects.all() ] 
               
                                
                                
                                
        department=[ dep.department_name for dep in Hospital_Department.objects.all()]
       
        response={
           
            "ug_course":list_of_ug_degree,
            "pg_course":list_of_pg_degree,
            "department":department,
            "ug_institute":ug_of_institute,
            "pg_institute":pg_of_institute,
            "hightest_qualification":hightest_qualification   
                }
        return Response(response,status=200)






"""USER EXPERIENCE POST AND GET HERE"""

class UserExperience(APIView):
    def get(self,request):
        username_id=request.GET.get('user_id')
        experience=request.GET.get('exp_id')
        if experience is not None:
            serializer=ExperienceSerializers(get_object_or_404(Experience,id=experience),many=False)
            return Response(serializer.data,status=200)
        elif username_id is not None:
            user=get_object_or_404(User,id=username_id)
            serializer=ExperienceSerializers(user.experience_set.all().order_by('-id'),many=True)
            return Response(serializer.data,status=200)
        else:
            return Response({"message":"something key errrors check and try agin"},status=404)

    def post(self,request):
        if not request.POST._mutable:
            request.POST._mutable = True 
        username_id=request.GET.get('user_id')
        data=request.data
        user=get_object_or_404(User,id=username_id)
    
        user.experience_set.create(hospital_name=data['hospital_name'],
                                designation=data['designation'], department=data['department'],
                                city=data['city'],start_date=data['start_date'],
                                end_date=data['end_date']
                                    )
        return Response({"message":"experience posted",'status':"true"},status=200)
    
    def put(self,request):
        exp=request.GET.get('exp_id')
        data=request.data 
        exp=Experience.objects.get(id=exp)
        serializers=ExperienceSerializers(exp,data=data,partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data,status=200)
        return Response(serializers.errors,status=404)

    def delete(self,request):
        exp=request.GET.get('exp_id')
        get_object_or_404(Experience,id=exp).delete()
        return Response({"message":"experience deleted","status":True},status=200)

        
"""GET AND POST RESUME UPLOAD"""
"""api/auth/upload/file/"""
class UserResumeUpload(APIView):
    parser_classes = ( JSONParser,MultiPartParser, FormParser)
    def get(self,request):
        response={}
        username_id=request.GET.get('user_id')
        user=get_object_or_404(User,id=username_id) 
        
        profile=Profile.objects.select_related('contact').get(contact__userdetail__id=user.id)
        resume_set=user.resumeupload_set.all()
        
        for resume in resume_set:
            response[resume.id]={
                "resume_id":resume.id,
                "upload_file":resume.upload_file.url if resume.upload_file else "no resume",
                "profile_name":profile.contact.profile_name,
                "phone_number":profile.contact.phone_number,
                "profileImage":profile.profileImage.url if profile.profileImage else "no image",
               
            }
        return Response(response.values(),status=200)

    def post(self,request):

        if not request.POST._mutable:
            request.POST._mutable = True
        
        data =ast.literal_eval(request.data['registerdata'])
      
        user=get_object_or_404(User,id=data['userid'])
        data['upload_file']=request.FILES['upload_file'] 
        print(data)
        serializer=ResumeUploadSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Document uploaded successfully","status":True},status=200)
        return Response(serializer.errors,status=400)
    
    def put(self,request):

        if not request.POST._mutable:
            request.POST._mutable = True
        resumeid=request.GET.get('resume_id')
        
        data =ast.literal_eval(request.data['registerdata'])
        try:
            get_resume_id=ResumeUpload.objects.get(id=resumeid)
        except ResumeUpload.DoesNotExist:
            return Response({"message":"resume id not found","status":"false"},status=404)
        data['upload_file']=request.FILES['upload_file'] 
        
        serializer=ResumeUploadSerializers(get_resume_id, data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Document uploaded successfully","status":True},status=200)
        return Response(serializer.errors,status=400)
    
    def delete(self,request):
        resume_id=request.GET.get('resume_id')
        get_object_or_404(ResumeUpload,id=resume_id).delete()
        return Response({"message":"file deleted","status":"true"},status=200) 





""" API FOR PROFILE ISO"""

"""api/user/profile/?user_id=12"""
class User_Profile_In_Ios_System(APIView):
    parser_class = (FileUploadParser,)
    def put(self,request):
        userid=request.GET.get('user_id')
        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True
        user=get_object_or_404(User,id=userid)
        if data.get('profile_name')!=user.first_name:
            profileName=data['profile_name']
            data['first_name']=profileName
            userserializer=UserSerializers(user,data=data,partial=True)
            if userserializer.is_valid():
                userserializer.save()
        contact =Identification.objects.get(userdetail__id=user.id)
        data["userdetail"]=user.id
        contactserializer=IdentificationSerializers(contact,data=data,partial=True)
        if contactserializer.is_valid():
            contactserializer.save()
        profile=Profile.objects.get(contact=contact)
        data['contact']=contact.id
        serializer=ProfileSerializers(profile,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=400)

"""IOS NEW ARTICAL POST"""
"""news/artical/post?user_id=171"""
class NewsArticalPost_Ios(APIView):
    parser_class = (FileUploadParser,)
    def post(self,request):
        userid=request.GET.get('user_id')
        
        if not request.POST._mutable:
            request.POST._mutable = True 
        data =request.data
        user=get_object_or_404(User,id=userid)
        data['userid']=user.id
        data['artical_image']=request.FILES['artical_image']
        serializer=NewsArticalPostSerializers(data=data)
       
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"news artical posted","status":True},status=200)
        return Response({"message":"errors","status":False},status=400)


"""ARTICAL POST pending work"""
class ArticalPost_ios(APIView):
    def post(self,request):
        userid=request.GET.get('user_id')
        
        if not request.POST._mutable:
            request.POST._mutable = True 
        data =request.data
        user=get_object_or_404(User,id=userid)
        data['user']=user.id
        data['mediafile']=request.FILES['mediafile']
        serializer=ArticalsSerializers(data=data)
       
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"artical posted","status":True},status=200)
        return Response({"message":serializer.errors,"status":False},status=400)

"""CASE POST"""
class ComplaintPost(APIView):
    def post(self,request):
        userid=request.GET.get('user_id')
        
        if not request.POST._mutable:
            request.POST._mutable = True 
        data =request.data
        user=get_object_or_404(User,id=userid)
        data['complaint_id']=user.id
        data['com_image']=request.FILES['com_image']
        serializer=ComplaintSerializers(data=data)
       
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"news artical posted","status":True},status=200)
        return Response({"message":serializer.errors,"status":False},status=400)

"""POLL POST"""
class PollPost(APIView):
    def post(self,request):
        userid=request.GET.get('user_id')
        
        if not request.POST._mutable:
            request.POST._mutable = True 
        data =request.data
        user=get_object_or_404(User,id=userid)
        data['poll_user']=user.id
        data['poll_image']=request.FILES['poll_image']
        serializer=PollSerializers(data=data)
       
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"poll posted","status":True},status=200)
        return Response({"message":serializer.errors,"status":False},status=400)


"""COLLEGE POST"""
class CollegeStoryPost(APIView):
    def post(self,request):
        userid=request.GET.get('user_id')
        
        if not request.POST._mutable:
            request.POST._mutable = True 
        data =request.data
        user=get_object_or_404(User,id=userid)
        data['user']=user.id
        data['photos']=request.FILES['photos']
        serializer=College_StorySerializers(data=data)
       
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"College story posted","status":True},status=200)
        return Response({"message":serializer.errors,"status":False},status=400)

""" END IOS CASE POST"""



############################################################################

"""HOW MANY CASE POSTED BY PARTICULAR USER"""
"""api/user/case?user=171"""
class User_Posted_Case(APIView):
    def get(Self,request):
        query=request.query_params
        
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            cases=user.complaint_set.all()
            for case in cases:
                status_data={
                    "bookmark_count":case.bookmark.count(),
                    "bookmark_status":case.bookmark.filter(id=user.id).exists(),
                    "like_count":case.likes.count(),
                    "like_status":case.likes.filter(id=user.id).exists(),

                            }

                serializer=ComplaintSerializers(case,many=False).data
                profile=Profile.objects.get(contact__userdetail__id=case.complaint_id.id)
                
                serializer.update(
                                {
                                    
                                    "username":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                    "discussions":case.discussions_set.all().count(),
                                    "follow":"uploader"
                                    
                                })
                serializer.update(status_data)
                response[case.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)

"""HOW MANY CASE BOOKMARK BY PARTICULAR USER"""
"""api/user/case/bookmarks?user_id=171"""
class User_Bookmark_Case(APIView):
    def get(Self,request):
        query=request.query_params
        print(query)
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            cases=Complaint.objects.filter(bookmark=user)
            for case in cases:
                status_data={
                    "bookmark_count":case.bookmark.count(),
                    "bookmark_status":case.bookmark.filter(id=user.id).exists(),
                    "like_count":case.likes.count(),
                    "like_status":case.likes.filter(id=user.id).exists(),

                            }
                profile=Profile.objects.get(contact__userdetail__id=case.complaint_id.id)
                serializer=ComplaintSerializers(case,many=False).data
                serializer.update(
                                    {
                               
                                "username":profile.contact.profile_name,
                                "current_job_location":profile.contact.current_job_location,
                                "speciality":profile.contact.speciality,
                                "hightest_qualification":profile.contact.hightest_qualification,
                                "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                "discussions":case.discussions_set.all().count(),
                                "follow":"uploader"
                                    }
                                )
                serializer.update(status_data)
                response[case.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)


"""HOW MANY CASE LIKES BY PARTICULAR USER"""
class User_Like_Case(APIView):
    def get(Self,request):
        query=request.query_params
       
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            cases=Complaint.objects.filter(likes=user)
            for case in cases:
                status_data={
                    "bookmark_count":case.bookmark.all().count(),
                    "bookmark_status":case.bookmark.filter(id=user.id).exists(),
                    "like_count":case.likes.all().count(),
                    "like_status":case.likes.filter(id=user.id).exists(),

                            }
                profile=Profile.objects.get(contact__userdetail__id=case.complaint_id.id)
                serializer=ComplaintSerializers(case,many=False).data
                serializer.update(
                                    {
                                        "username":profile.contact.profile_name,
                                        "current_job_location":profile.contact.current_job_location,
                                        "speciality":profile.contact.speciality,
                                        "hightest_qualification":profile.contact.hightest_qualification,
                                        "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                        "discussions":case.discussions_set.all().count(),
                                        "follow":"uploader"

                                        
                                    }
                                )
                serializer.update(status_data)
                response[case.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)

"""HOW MANY NEWS POSTED BY PARITICULAR USE"""
"""api/user/news?user_id=171"""
class User_Posted_News(APIView):
    def get(Self,request):
        query=request.query_params
       
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            newsposts=NewsArticalPost.objects.filter(userid=user)
            for newspost in newsposts:
                status_data={
                    "bookmark_count":newspost.bookmark.all().count(),
                    "bookmark_status":newspost.bookmark.filter(id=user.id).exists(),
                    "like_count":newspost.likes.count(),
                    "like_status":newspost.likes.filter(id=user.id).exists(),

                            }
                profile=Profile.objects.get(contact__userdetail__id=newspost.userid.id)
                serializer=NewsArticalPostSerializers(newspost,many=False).data
                serializer.update(
                                {
                                    "username":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                    "follow":"uploader"
                                })
                serializer.update(status_data)
                response[newspost.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)


"""HOW MANY  NEWS BOOKMARK BY PARTICULAR USER"""
class User_News_Bookmarks(APIView):
    def get(self,request):
        query=request.query_params
        print(query['user_id'])
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            newsposts=NewsArticalPost.objects.filter(bookmark=user)
            for newspost in newsposts:
                status_data={
                    "bookmark_count":newspost.bookmark.all().count(),
                    "bookmark_status":newspost.bookmark.filter(id=user.id).exists(),
                    "like_count":newspost.likes.count(),
                    "like_status":newspost.likes.filter(id=user.id).exists(),

                            }
                profile=Profile.objects.get(contact__userdetail__id=newspost.userid.id)
                serializer=NewsArticalPostSerializers(newspost,many=False).data
                serializer.update({
                                    "username":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                    
                                    })
                serializer.update(status_data)
                response[newspost.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)


"""HOW MANY NEWS LIKED NEWS BY PARTICULAR USER"""
class User_News_LIke(APIView):
    def get(self,request):
        query=request.query_params
        print(query['user_id'])
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            newsposts=NewsArticalPost.objects.filter(likes=user)
            for newspost in newsposts:
                status_data={
                    "bookmark_count":newspost.bookmark.all().count(),
                    "bookmark_status":newspost.bookmark.filter(id=user.id).exists(),
                    "like_count":newspost.likes.count(),
                    "like_status":newspost.likes.filter(id=user.id).exists(),

                            }
                profile=Profile.objects.get(contact__userdetail__id=newspost.userid.id)
                serializer=NewsArticalPostSerializers(newspost,many=False).data
                serializer.update(
                                {
                                    "username":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                })
                serializer.update(status_data)
                response[newspost.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)


"""HOW MANY ARTICAL POSTED BY PARTICULAR USER"""
class User_Posted_Artical(APIView):
    def get(Self,request):
        query=request.query_params
        
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            articals=user.articals_set.all()
            for artical in articals:
                status_data={
                    "bookmark_count":artical.bookmark.count(),
                    "bookmark_status":artical.bookmark.filter(id=user.id).exists(),
                    "like_count":artical.likes.count(),
                    "like_status":artical.likes.filter(id=user.id).exists(),

                            }

                serializer=ArticalsSerializers(artical,many=False).data
                profile=Profile.objects.get(contact__userdetail__id=artical.user.id)
                
                serializer.update(
                                {
                                    "username":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                    "follow":"uploader"
                                    
                                })
                serializer.update(status_data)
                response[artical.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)


"""HOW MANY  ARTICAL BOOKMARK BY PARTICULAR USER"""
class User_Artical_Bookmarks(APIView):
    def get(self,request):
        query=request.query_params
        print(query['user_id'])
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            articals=Articals.objects.filter(bookmark=user)
            for artical in articals:
                status_data={
                    "bookmark_count":artical.bookmark.all().count(),
                    "bookmark_status":artical.bookmark.filter(id=user.id).exists(),
                    "like_count":artical.likes.count(),
                    "like_status":artical.likes.filter(id=user.id).exists(),

                            }
                profile=Profile.objects.get(contact__userdetail__id=artical.user.id)
                serializer=ArticalsSerializers(artical,many=False).data
                serializer.update({
                        "username":profile.contact.profile_name,
                        "current_job_location":profile.contact.current_job_location,
                        "speciality":profile.contact.speciality,
                        "hightest_qualification":profile.contact.hightest_qualification,
                        "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                        
                        })
                serializer.update(status_data)
                response[artical.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)


"""HOW MANY ARTICAL LIKED NEWS BY PARTICULAR USER"""
class User_Artical_LIke(APIView):
    def get(self,request):
        query=request.query_params
        
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            articals=Articals.objects.filter(likes=user)
            for artical in articals:
                status_data={
                    "bookmark_count":artical.bookmark.all().count(),
                    "bookmark_status":artical.bookmark.filter(id=user.id).exists(),
                    "like_count":artical.likes.count(),
                    "like_status":artical.likes.filter(id=user.id).exists(),

                            }
               
                serializer=ArticalsSerializers(artical,many=False).data
                profile=Profile.objects.get(contact__userdetail__id=artical.user.id)
                serializer.update({
                                    "username":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "profile_image":profile.profileImage.url if profile.profileImage else "no image",

                                    })
                serializer.update(status_data)
                response[artical.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)



"""HOW MANY COLLEGE STORY POSTED BY PARTICULAR USER"""
class User_College_Story_Posted(APIView):
    def get(Self,request):
        query=request.query_params
        
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            collegestorys=user.college_story_set.all()
            for collegestroy in collegestorys:
                status_data={
                    "bookmark_count":collegestroy.bookmark.count(),
                    "bookmark_status":collegestroy.bookmark.filter(id=user.id).exists(),
                    "like_count":collegestroy.likes.count(),
                    "like_status":collegestroy.likes.filter(id=user.id).exists(),

                            }

                serializer=College_StorySerializers(collegestroy,many=False).data
                profile=Profile.objects.get(contact__userdetail__id=collegestroy.user.id)
                
                serializer.update(
                                {
                                    "username":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                    "follow":"uploader"
                                    
                                })
                serializer.update(status_data)
                response[collegestroy.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)


"""HOW MANY  ARTICAL BOOKMARK BY PARTICULAR USER"""
class User_College_Stroy_Bookmarks(APIView):
    def get(self,request):
        query=request.query_params
        print(query['user_id'])
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            storys=College_Story.objects.filter(bookmark=user)
            for story in storys:
                status_data={
                    "bookmark_count":story.bookmark.all().count(),
                    "bookmark_status":story.bookmark.filter(id=user.id).exists(),
                    "like_count":story.likes.count(),
                    "like_status":story.likes.filter(id=user.id).exists(),

                            }

                serializer=College_StorySerializers(story,many=False).data
                profile=Profile.objects.get(contact__userdetail__id=story.user.id)
                
                serializer.update(
                                {
                                    "username":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                    "follow":"uploader"
                                    
                                })
                serializer.update(status_data)
                response[story.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)


"""HOW MANY COLLEGE STOTRY LIKED  BY PARTICULAR USER"""
class User_College_Story_LIke(APIView):
    def get(self,request):
        query=request.query_params
        
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            collegestorys=College_Story.objects.filter(likes=user)
            for collegestory in collegestorys:
                status_data={
                    "bookmark_count":collegestory.bookmark.all().count(),
                    "bookmark_status":collegestory.bookmark.filter(id=user.id).exists(),
                    "like_count":collegestory.likes.count(),
                    "like_status":collegestory.likes.filter(id=user.id).exists(),

                            }

                serializer=College_StorySerializers(collegestory,many=False).data
                profile=Profile.objects.get(contact__userdetail__id=collegestory.user.id)
                
                serializer.update(
                                {
                                    "username":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                    "follow":"uploader"
                                    
                                })
                serializer.update(status_data)
                response[collegestory.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)




"""HOW MANY POLL POSTED BY PARTICULAR USER"""
class User_Poll_Posted(APIView):
    def get(Self,request):
        query=request.query_params
        
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            polls=user.poll_set.all()
            for poll in polls:
                user_poll_status=poll.pollvote_set.filter(profile=user)
                status_data={
                    "bookmark_count":poll.bookmark.count(),
                    "bookmark_status":poll.bookmark.filter(id=user.id).exists(),
                    "like_count":poll.likes.count(),
                    "like_status":poll.likes.filter(id=user.id).exists(),
                    "user_status":user_poll_status.exists(),
                    "vote":poll.pollvote_set.all().count(),
                    "A":poll.pollvote_set.filter(choice="A").count(),
                    "B":poll.pollvote_set.filter(choice="B").count(),
                    "C":poll.pollvote_set.filter(choice="C").count(),
                    "D":poll.pollvote_set.filter(choice="D").count(),
                    "choice": user_poll_status[0].choice if user_poll_status.exists() else "no_opinion"

                            }

                serializer=PollSerializers(poll,many=False).data
                profile=Profile.objects.get(contact__userdetail__id=poll.poll_user.id)
                
                serializer.update(
                                {
                                    "username":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                    "follow":"uploader"
                                    
                                })
                serializer.update(status_data)
                response[poll.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)



"""HOW MANY  POLL BOOKMARK BY PARTICULAR USER"""
class User_Poll_Bookmarks(APIView):
    def get(self,request):
        query=request.query_params
        print(query['user_id'])
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            polls=Poll.objects.filter(bookmark=user)
            for poll in polls:
                user_poll_status=poll.pollvote_set.filter(profile=user)
                status_data={
                    "bookmark_count":poll.bookmark.all().count(),
                    "bookmark_status":poll.bookmark.filter(id=user.id).exists(),
                    "like_count":poll.likes.count(),
                    "like_status":poll.likes.filter(id=user.id).exists(),
                    "user_status":user_poll_status.exists(),
                    "vote":poll.pollvote_set.all().count(),
                    "A":poll.pollvote_set.filter(choice="A").count(),
                    "B":poll.pollvote_set.filter(choice="B").count(),
                    "C":poll.pollvote_set.filter(choice="C").count(),
                    "D":poll.pollvote_set.filter(choice="D").count(),
                    "choice": user_poll_status[0].choice if user_poll_status.exists() else "no_opinion"

                            }

                serializer=PollSerializers(poll,many=False).data
                profile=Profile.objects.get(contact__userdetail__id=poll.poll_user.id)
                
                serializer.update(
                                {
                                   
                                    "username":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                    "follow":"uploader"
                                    
                                })
                serializer.update(status_data)
                response[poll.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)


"""HOW MANY COLLEGE STOTRY LIKED  BY PARTICULAR USER"""
class User_Poll_LIke(APIView):
    def get(self,request):
        query=request.query_params
        
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            polls=Poll.objects.filter(likes=user)
            for poll in polls:
                user_poll_status=poll.pollvote_set.filter(profile=user)
                status_data={
                    "bookmark_count":poll.bookmark.all().count(),
                    "bookmark_status":poll.bookmark.filter(id=user.id).exists(),
                    "like_count":poll.likes.count(),
                    "like_status":poll.likes.filter(id=user.id).exists(),
                    "user_status":user_poll_status.exists(),
                    "vote":poll.pollvote_set.all().count(),
                    "A":poll.pollvote_set.filter(choice="A").count(),
                    "B":poll.pollvote_set.filter(choice="B").count(),
                    "C":poll.pollvote_set.filter(choice="C").count(),
                    "D":poll.pollvote_set.filter(choice="D").count(),
                    "choice": user_poll_status[0].choice if user_poll_status.exists() else "no_opinion"
                    

                            }

                serializer=PollSerializers(poll,many=False).data
                profile=Profile.objects.get(contact__userdetail__id=poll.poll_user.id)
                
                serializer.update(
                                {
                                    "username":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "profile_image":profile.profileImage.url if profile.profileImage else "no image",
                                    "follow":"uploader"
                                    
                                })  
                serializer.update(status_data)
                response[poll.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)

##########################################################################



"""api/subject/"""
'''job show by all course and search by course'''
class Subjects(APIView):
    
    def get(self,request,format=None):
        
        course_name=request.GET.get('course')
        username_id=request.GET.get('user_id')
        location=request.GET.get('location').split(",") if request.GET.get('location') is not None else request.GET.get('location')

        resp={}
       
        if course_name :
            if course_name and location:
               user_query=Q(course__iexact=course_name,location__in=location)
            elif course_name and username_id:
                user_query=Q(course__iexact=course_name)
            
            user=get_object_or_404(User,id=username_id)

            job_category=Category_Related_Job.objects.filter(user_query).order_by('-created_date')
            
            
            for category in job_category:
                serializer=Category_Related_JobSerializers(category,many=False).data
                resp[category.id]=serializer
               
                resp[category.id].update({
                    "bookmark_status":category.bookmark.filter(id=user.id).exists(),
                    "like_status":category.likes.filter(id=user.id).exists(), 
                    "apply_status":category.applicant.filter(id=user.id).exists(),
                        })
                
            return Response(resp.values(),status=200)
        
        else:
            subject=list(Subject.objects.all())
           
            for sub in subject:
                category=sub.category_releted_job_set.all()
               
                if category:    
                    resp[sub.id]={
                        "id":sub.id,
                        "course":sub.name,
                        "image":sub.image.url if sub.image else "image not avaialble",
                        "total":category.count()
                    }
            return Response(resp.values(),status=200)
            

    def post(self,request,format=None):
        data=request.data 
        serializers=SubjectSerializers(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data,status=201)
        return Response(serializers.errors,status=200)


    def put (self,request,format="json"):
        data=request.data 
        subjectId=request.GET.get('subjectid')
        if subjectId:
            try:
                subject=Subject.objects.get(id=subjectId)
                if data.get('image'):
                    subject.image.delete()
                    subject.image=data.get('image')
                serializers=SubjectSerializers(subject,data=data,partial=True)
                if serializers.is_valid():
                    serializers.save()
                    return Response(serializers.data,status=200)
                return Response(serializers.errors,status=400)
            except Exception as e:
                return Response({"message":"subject id not found","status":"false"},status=400)
        else:
            return Response({"message":"something you passing wrong","status":"false"},status=400)
    
    def delete (self,request):
        data=request.data 
        subjectId=request.GET.get('subjectid')
        if subjectId:
            try:
                subject=Subject.objects.get(id=subjectId).delete()
                return Response({"message":"subject id deleted successfully","status":"true"},status=200)
            except Exception as e:
                 return Response({"message":"subject id not found","exception":str(e),"status":"false"},status=400)
        else:
            return Response({"message":"something you passing wrong","status":"false"},status=400)




'''api/job/category/'''
'''category of job just like covid duety'''
class New_Job_Category_Post(APIView):
    def get(self,request,format=None): 
        job_category=Job_By_Category.objects.all()
        return Response(Job_By_CategorySerializers(job_category,many=True).data,status=200)
    
    
    
'''api/new/job/'''
'''new job post'''
class New_Job_Post(APIView):
    
    def get(self,request):
        data=request.data 
        categoryId=request.GET.get('categoryid')
        new_job_id=request.GET.get('jobid')
        username_id=request.GET.get('user_id')
        location=request.GET.get('location').split(",") if request.GET.get('location') is not None else request.GET.get('location')
        department=request.GET.get('department').split(",") if request.GET.get('department') is not None else request.GET.get('department')
      
        resp={}


        try:
            user=User.objects.get(id=username_id)
        except Exception as e:
            return Response({"message":"user not found"},status=400)
        
        if categoryId:
            
            try:
                
                category=Job_By_Category.objects.get(id=categoryId)
            
            except Exception as e:
                
                return Response({"message":"categoryid not exists","exception":str(e)},status=404) 
            
            if department and location:
                user_query=Q(category__id=category.id,location__in=location,department__in=department)
               
            elif department:
                user_query=Q(category__id=category.id,department__in=department)
                
                
            elif location:
               user_query=Q(category__id=category.id,location__in=location)
               
            else:

                user_query=Q(category__id=category.id)

            
            
            new_job=Category_Related_Job.objects.select_related('category').filter(user_query,job_status=True).order_by('-created_date')
            
            for categorys in new_job:
             
                serializer=Category_Related_JobSerializers(categorys,many=False).data
                resp[categorys.id]=serializer
               
                resp[categorys.id].update({
                        
                            "bookmark_status":categorys.bookmark.filter(id=user.id).exists(),
                            "like_status":categorys.likes.filter(id=user.id).exists(), 
                            "apply_status":categorys.applicant.filter(id=user.id).exists(),
                                        })
                
            return Response(resp.values(),status=200)
        
        elif new_job_id and username_id:
           
            
            try:
                jobid=Category_Related_Job.objects.get(id=new_job_id)
            except Exception as e:
                return Response({"message":"job not exists","exception":str(e)},status=404) 
            
            serializer=Category_Related_JobSerializers(jobid,many=False).data
           
            serializer.update({
                            "bookmark_status":jobid.bookmark.filter(id=user.id).exists(),
                            "like_status":jobid.likes.filter(id=user.id).exists(), 
                            "apply_status":jobid.applicant.filter(id=user.id).exists(),
                            })
            return Response(serializer,status=200)  
               
        
        elif  username_id:
            
            
            job_id=Category_Related_Job.objects.filter(job_status=True).order_by('-created_date')
           
            for category in job_id:
                resp[category.id]=Category_Related_JobSerializers(category,many=False).data
                resp[category.id].update({
                        "bookmark_status":  category.bookmark.filter(id=username_id).exists() ,
                        "like_status":category.likes.filter(id=username_id).exists(), 
                        "apply_status":category.applicant.filter(id=username_id).exists(),
                                        })
                
            return Response(resp.values(),status=200)
        else:
            return Response({"message":"Key errors something passing wrong"},status=400)
            
   
    
"""api/job/top/"""        
class TopJob(APIView):
    def get(self,request):
        resp={}
        username_id=request.GET.get('user_id')
        job_id=Category_Related_Job.objects.filter(top_job=True).order_by('-created_date')
       
        for category in job_id:
            resp[category.id]=Category_Related_JobSerializers(category,many=False).data
            resp[category.id].update({
                    "bookmark_status":  category.bookmark.filter(id=username_id).exists() ,
                    "like_status":category.likes.filter(id=username_id).exists(), 
                    "apply_status":category.applicant.filter(id=username_id).exists(),
                                    })
            
        return Response(resp.values(),status=200)


""""DESIGNATION GET POST """  

class All_Designations(APIView):
    def get(self,request):
        departmentid=request.GET.get('department_id')
        designations=Designation.objects.all()
        if departmentid:
            return Response(DesignationSerializers(designations.get(id=departmentid),many=False).data)
        return Response(DesignationSerializers(designations,many=True).data)

"""HIGHER QUALIFICTION"""       
class DoctorHigherQualification(APIView):
    def get(self,request):
        serializers=HigherQualificationSerializers(HigherQualification.objects.all(),many=True)
        return Response(serializers.data,status=200)

"""STATE"""
class State_Location(APIView):
    def get(self,request):
        serializers=StateSerializers(State.objects.all(),many=True)
        return Response(serializers.data,status=200)


"""CITY"""
class City_Location(APIView):
    def get(self,request):
        response={}
        for state in State.objects.all():
            response[state.id]={
                "id":state.id,
                "name":state.name,
                "city":[{"id":area.id,"name":area.hospital_city_name} for area in state.city_set.all() ]
            }
        return Response(response.values(),status=200)


from listdata.collegedata import *
"""UNDER GRADUCATION DEGREE"""
class Under_Graduation_Degree_List(APIView):
    def get(self,request):
        response={}
        for i in range(len(list_of_ug_degree)):
            response[i]={
                "id":i+1,
                "degree":list_of_ug_degree[i]
            }
        return Response(response.values())

"""UNDER GRADUCATION DEGREE COLLEDE /INSTITUTE"""
class Under_Graduation_Degree_insttute_List(APIView):
    def get(self,request):
        response={}
        for i in range(len(ug_of_institute)):
            response[i]={
                "id":i+1,
                "institute":ug_of_institute[i]
            }
        return Response(response.values())


"""POST GRADUCATION DEGREE """
class Post_Graduation_Degree_List(APIView):
    def get(self,request):
        response={}
        for i in range(len(list_of_pg_degree)):
            response[i]={
                "id":i+1,
                "degree":list_of_pg_degree[i]
            }
        return Response(response.values())


"""POST GRADUCATION INSTITUTE"""
class Post_Graduation_Degree_institute_List(APIView):
    def get(self,request):
        response={}
        for i in range(len(pg_of_institute)):
            response[i]={
                "id":i+1,
                "institute":pg_of_institute[i]
            }
        return Response(response.values())


class Specility_Department_list(APIView):
    def get(self,request):
        response={}
        H_and_D=Hospital_Department.objects.all()
        for hd in H_and_D:
                
            response[hd.id]={
                "id":hd.id,
                "department":hd.department_name,
                
            }
           
        return Response(response.values())

"""GENDER """
class Gender(APIView):
    def get(self,request):
        response={}
        for i in range(len(gender)):
            response[i]={
                "id":i+1,
                "gender":gender[i]
            }
        return Response(response.values())

"""LANGUAGE"""
class Languages(APIView):
    def get(self,request):
        response={}
        for i in range(len(language)):
            response[i]={
                "id":i+1,
                "language":language[i]
            }
        return Response(response.values())

#############################LIKE BOOKMARK FOLLOW AND UNFOLLOW######################################

""""LIKE BOOKMARK AND APPLY JOB"""
class Likes(APIView):
    def get(self,request,format=None):
        username_id=request.GET.get('user_id')
        category_job_id=request.GET.get('job_id')
        try:
            user=User.objects.get(id=username_id)
            
        except Exception as e:
            return Response({"message":str(e)})
        try:
            Category_Related_Job.objects.get(id=category_job_id,likes=user) 
            return Response({"like_status":"true"})  
        except Exception as e:
             return Response({"like_status":"false"})
        
    def post(self,request,format="json"):
        username_id=request.GET.get('user_id')
        category_job_id=request.GET.get('job_id')
        complaintId=request.GET.get('complaint_id')
        pollId=request.GET.get('poll_id')
        articalID=request.GET.get('art_id')
        new_articalId=request.GET.get('artical_id')

        
        try:
            user=User.objects.get(id=username_id)
        except Exception as e:
            return Response({"message":str(e)})

        if username_id and category_job_id:
            
               
            try:
                job_likes=Category_Related_Job.objects.get(id=category_job_id)
            except Exception as e:
                return Response({"message":"jobs id not found","status":"false","exception":str(e)},status=400)
            try:
                if job_likes.likes.get(id=user.id):
                    job_likes.likes.remove(user)
                    return Response({"like_status":"false","like_count":job_likes.likes.all().count()},status=200)
            except Exception as e:
                job_likes.likes.add(user)
                return Response({"like_status":"true","like_count":job_likes.likes.all().count()},status=200)
            return Response({"message":"error find check and try again","status":"true"},status=400)
        
        elif username_id and complaintId:
            
           
            try:
                complaint=Complaint.objects.get(id=complaintId)
            except Exception as e:
                return Response({"message":"complaint id not found","status":"false","exception":str(e)},status=400)
            try:
                if complaint.likes.get(id=user.id):
                    complaint.likes.remove(user)
                    return Response({"like_status":"false","like_count":complaint.likes.all().count()},status=200)
            except Exception as e:
                complaint.likes.add(user)
                return Response({"like_status":"true","like_count":complaint.likes.all().count()},status=200)
            return Response({"message":"error find check and try again","status":"true"},status=400)

        elif username_id and pollId:
            
            try:
                poll=Poll.objects.get(id=pollId)
            except Exception as e:
                return Response({"message":"poll id not found","status":"false","exception":str(e)},status=400)
            try:
                if poll.likes.get(id=user.id):
                    poll.likes.remove(user)
                    return Response({"poll_like_status":"false","like_count":poll.likes.all().count()},status=200)
            except Exception as e:
                poll.likes.add(user)
                return Response({"poll_like_status":"true","like_count":poll.likes.all().count()},status=200)
            return Response({"message":"error find check and try again","status":"true"},status=400)

        elif username_id and new_articalId:
            
            try:
                artical=NewsArticalPost.objects.get(id=new_articalId)
            except Exception as e:
                return Response({"message":"News Artical id not found","status":"false","exception":str(e)},status=400)
            try:
                if artical.likes.get(id=user.id):
                    artical.likes.remove(user)
                    return Response({"news_like_status":"false","like_count":artical.likes.all().count()},status=200)
            except Exception as e:
                artical.likes.add(user)
                return Response({"news_like_status":"true","like_count":artical.likes.all().count()},status=200)
            return Response({"message":"error find check and try again","status":"true"},status=400)

        elif username_id and articalID:
            
            try:
                artical=Articals.objects.get(id=articalID)
            except Exception as e:
                return Response({"message":"Artical id not found","status":"false","exception":str(e)},status=400)
            try:
                if artical.likes.get(id=user.id):
                    artical.likes.remove(user)
                    return Response({"like_status":"false","like_count":artical.likes.all().count()},status=200)
            except Exception as e:
                artical.likes.add(user)
                return Response({"like_status":"true","like_count":artical.likes.all().count()},status=200)
            return Response({"message":"error find check and try again","status":"true"},status=400)

        else:
            return Response({"errors":"key error","status":"false"},status=200)

'''Add bookmark'''
'''api/job/bookmark/'''    
class BookMark(APIView):
    def get(self,request,format=None):
        username_id=request.GET.get('user_id')
        
        resp={}
        try:
            user=User.objects.get(id=username_id)
        except Exception as e:
            return Response({"message":str(e)})
       
        job_categorys=Category_Related_Job.objects.filter(bookmark=user)
        
        for category in job_categorys:
            
            serializer=Category_Related_JobSerializers(category,many=False).data
            resp[category.id]=serializer
            resp[category.id].update({
                "bookmark_status":category.bookmark.filter(id=user.id).exists(),
                "like_status":category.likes.filter(id=user.id).exists(), 
                "apply_status":category.applicant.filter(id=user.id).exists(),
                })
           
        return Response(resp.values(),status=200)
       
           
    
    def post(self,request,format="json"):
        username_id=request.GET.get('user_id')
        category_job_id=request.GET.get('job_id')
        news_arctical=request.GET.get('artical_id')
        articalID=request.GET.get('art_id')
        poll=request.GET.get('poll_id')
        complaint=request.GET.get('complaint_id')
        pageNews=request.GET.get('pagenews_id')

        try:
            user=User.objects.get(id=username_id)
        except Exception as e:
            return Response({"message":str(e)})
        
        if username_id and category_job_id:
            try:
                job_likes=Category_Related_Job.objects.get(id=category_job_id)
            except Exception as e:
                return Response({"message":"jobs id not found","status":"false","exception":str(e)},status=400)
            try:
                if job_likes.bookmark.get(id=user.id):
                    job_likes.bookmark.remove(user)
                    return Response({"bookmark_status":"false"},status=200)
            except Exception as e:
                job_likes.bookmark.add(user)
                return Response({"bookmark_status":"true"},status=200)
        
        elif username_id and news_arctical:
            try:
                artical=NewsArticalPost.objects.get(id=news_arctical)
            except Exception as e:
                return Response({"message":"News Artical id not found","status":"false","exception":str(e)},status=400)
            try:
                if artical.bookmark.get(id=user.id):
                    artical.bookmark.remove(user)
                    return Response({"bookmark_status":"false"},status=200)
            except Exception as e:
                artical.bookmark.add(user)
                return Response({"bookmark_status":"true"},status=200)

        elif username_id and articalID:
            try:
                artical=Articals.objects.get(id=articalID)
            except Exception as e:
                return Response({"message":"Artical id not found","status":"false","exception":str(e)},status=400)
            try:
                if artical.bookmark.get(id=user.id):
                    artical.bookmark.remove(user)
                    return Response({"bookmark_status":"false"},status=200)
            except Exception as e:
                artical.bookmark.add(user)
                return Response({"bookmark_status":"true"},status=200)

        elif username_id and poll:
            try:
                single_poll=Poll.objects.get(id=poll)
            except Exception as e:
                return Response({"message":"poll id not found","status":"false","exception":str(e)},status=400)
            try:
                if single_poll.bookmark.get(id=user.id):
                    single_poll.bookmark.remove(user)
                    return Response({"bookmark_status":"false"},status=200)
            except Exception as e:
                single_poll.bookmark.add(user)
                return Response({"bookmark_status":"true"},status=200)

        
        elif username_id and complaint:
            try:
                case=Complaint.objects.get(id=complaint)
            except Exception as e:
                return Response({"message":"complaint id not found","status":"false","exception":str(e)},status=400)
            try:
                if case.bookmark.get(id=user.id):
                    case.bookmark.remove(user)
                    return Response({"bookmark_status":"false"},status=200)
            except Exception as e:
                case.bookmark.add(user)
                return Response({"bookmark_status":"true"},status=200)
        
        



        return Response({"message":"error find check and try again","status":"true"},status=400)

"""GET FOLLOWING PROFILE"""
class FollowingProfile(APIView):
    def get(self,request):
        username_id=request.GET.get('user_id')
        response={}
        try:
            followingprofile=Profile.objects.filter(follow=get_object_or_404(User,id=username_id))
        except Exception as e:
            return Response({"message":str(e)})
        for followering in followingprofile:
            
            response[followering.id]={
                "following_id":followering.contact.userdetail.id,
                "username":followering.contact.userdetail.username,
                "profile_name":followering.contact.profile_name,
                "profileImage": followering.profileImage.url if followering.profileImage else "no image"
            }
        return Response(response.values(),status=status.HTTP_200_OK)

"""FOLLOW AND UNFOLLOW API"""
class TryToFollowUnfollow(APIView):
    def get(self,request):
        username_id=request.GET.get('user_id')
        response={}
        try:
            author=Profile.objects.select_related('contact').get(contact__userdetail__id=username_id)
        except Exception as e:
            return Response({"message":str(e)})
        for follower in author.follow.all():
            pro=Profile.objects.get(contact__userdetail__id=follower.id)
            response[follower.id]={
                "username":follower.username,
                "profile_name":pro.contact.profile_name,
                "profileImage": pro.profileImage.url if pro.profileImage else "no image"
            }
        return Response(response.values(),status=status.HTTP_200_OK)
        
    def post(self,request,format="json"):
        username_id=request.GET.get('user_id')
        followid=request.GET.get('follow_id')#author
        if username_id != followid:
            try:
                user=User.objects.get(id=username_id)
            except Exception as e:
                return Response({"message":str(e)})
            
            try:
                author=Profile.objects.select_related('contact').get(contact__userdetail__id=followid)
            except Exception as e:
                return Response({"message":"follow id not found","status":"false","exception":str(e)},status=400)
            try:
                if author.follow.get(id=user.id):
                    author.follow.remove(user)
                    return Response({"follow":"false"},status=200)
            except Exception as e:
                author.follow.add(user)
                return Response({"follow":"true"},status=200)
        else:
            return Response({"message":"you can not follow own profile","status":"false"},status=400)


########################################################END BLOCK OF FOLLOW AND BOOKMARK LIKE#####################

"""APPLY FOR JOB"""
'''api/job/apply/'''
class Jobs_Applies(APIView):
    
    def get(self,request,format=None):
        username_id=request.GET.get('user_id')
        resp={}
        try:
            user=User.objects.get(id=username_id)
        except Exception as e:
            return Response({"message":str(e)})
       
        job_categorys=Category_Related_Job.objects.filter(applicant=user)
        
        for category in job_categorys:
            
            serializer=Category_Related_JobSerializers(category,many=False).data
            resp[category.id]=serializer
            like=category.likes.filter(id=user.id)
            bookmark=category.bookmark.filter(id=user.id)
            apply=category.applicant.filter(id=user.id)
            resp[category.id].update({
                "bookmark_status":bookmark.exists(),
                "like_status":like.exists(), 
                "apply_status":apply.exists(),
                })
            
           
        return Response(resp.values(),status=200)
    
    def post(self,request,format="json"):
        username_id=request.GET.get('user_id')
        category_job_id=request.GET.get('job_id')
        try:
            user=User.objects.get(id=username_id)
        except Exception as e:
            return Response({"message":str(e)})
           
        try:
            job_application=Category_Related_Job.objects.get(id=category_job_id)
        except Exception as e:
            return Response({"message":"jobs id not found","status":"false","exception":str(e)},status=400)
        try:
            if job_application.applicant.get(id=user.id):
                job_application.applicant.remove(user)
                return Response({"apply_status":False},status=200)
        except Exception as e:
            job_application.applicant.add(user)
            return Response({"apply_status":True},status=200)
        return Response({"message":"error find check and try again","status":"true"},status=400)
        
class News_Category(APIView):
    def get(self,request):
        
        return Response(CategorySerializers(Category.objects.filter(status=True),many=True).data,status=200)

class Related_TO_News_Category(APIView):
    
    def get(self,request):
        category_id=request.GET.get('categoryid')
        news_id=request.GET.get('newsid')
        response={}
        if category_id:
            try:
                news_category=Category.objects.get(id=category_id,status=True)
            except Exception as e:
                return Response({"message":str(e)})
            serializers1=CategorySerializers(news_category,many=False).data 
            news=news_category.newsartical_set.filter(visiable=True).order_by('-created_date')
           
            
            for n in news:
                response[n.id]=NewsArticalSerializers(n,many=False).data
                response[n.id].update({"category":news_category.news_title})
           
            
            return Response(response.values(),status=200)
        elif news_id:
            news=NewsArtical.objects.get(id=news_id)
            serializers1=NewsArticalSerializers(news,many=False).data
            response[news.id]=serializers1
            response[news.id].update({"category":news.news.news_title})
            
            return Response(response.values(),status=200)
        
        else:
            return Response({"message":"something error wait for update"},status=400)






 
"""POLL POST ,VOTE FOR POLL AND COMMENT ON POLL API START HERE"""
class News_Poll(APIView):
    def get(self,request):
        response={}
        single_poll=request.GET.get('poll_id')
        if single_poll:
            poll=Poll.objects.get(id=single_poll)
            serializer=PollSerializers(poll,many=False).data
            pro=Profile.objects.select_related('contact').get(contact__userdetail__id=poll.poll_user.id)
            serializer1=ProfileSerializers(pro,many=False).data
            reg_profile=get_object_or_404(Identification,userdetail=pro.contact)
            reg_serializer=IdentificationSerializers(reg_profile,many=False).data
            serializer.update(serializer1)
            serializer.update(reg_serializer)
            response=serializer
            return Response(response,status=200)
    def post(self,request):
        data=request.data 
        if not request.POST._mutable:
            request.POST._mutable = True
        # data = ast.literal_eval(request.data['registerdata'])
        # data['poll_image']=request.FILES['poll_image']
        data=request.data
        serializer=PollSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"news artical posted","status":True},status=200)
        return Response({"message":"errors","status":False},status=400)

class VoteForPoll(APIView):
    def post(self,request):
        data=request.data
        poll=get_object_or_404(Poll,id=data['poll_id'])
        user=get_object_or_404(User,id=data['profile'])

        find_existing_voter_or_not=PollVote.objects.select_related('poll_id','profile').filter(poll_id__id=data['poll_id'],profile__id=data['profile'])
        if find_existing_voter_or_not.exists()==False:
            vote=PollVote.objects.create(poll_id=poll,profile=user,choice=data['choice'])
        # elif find_existing_voter_or_not.exists():
        #     vote=find_existing_voter_or_not.update(poll_id=poll,profile=user,choice=data['choice'])

        total_vote_on_this_poll=poll.pollvote_set.count()
        
        """CACULATING PERCENTAGE OF CHOICE"""
        choice={}
        for option in ["A","B","C","D"]:
            options_count=poll.pollvote_set.filter(choice=option).count()
            
            if (options_count != 0):
                choice.update({option:int((options_count/total_vote_on_this_poll)*100)})
            else:
                
                choice.update({option:options_count})

    
        return Response({"message":"Thank for opinion",
                        "votes":total_vote_on_this_poll,
                        "A":choice["A"], "B":choice["B"], "C":choice["C"], "D":choice["D"],
                        "choice":data['choice'],
                        })

class Poll_Comment(APIView):

    def get(self,request):
        response={}
        pollid=request.GET.get('poll_id')
        username_id=request.GET.get('user_id')
        commentId=request.GET.get('comment_id')

        
        if pollid is not None and username_id is not None:
            try:
                profile_detail=Profile.objects.get(contact__userdetail__id=username_id)
            except Exception as msg:
                return Response({"message":str(msg)})
            poll_comment=PollComment.objects.select_related('poll_id').filter(poll_id__id=pollid,profile__id=username_id).order_by("-id")
            
            if poll_comment.exists():
                for poll in poll_comment:
                    response[poll.id]={
                    "comment_id":poll.id,
                    "comment":poll.comment,
                    "profile":profile_detail.profileImage.url if profile_detail.profileImage else "no image",
                    "profile_name":profile_detail.contact.profile_name,
                    "agree":poll.agree.filter(id=username_id).exists(),
                    "disagree":poll.disagree.filter(id=username_id).exists(),
                    "agree_count":poll.agree.count(),
                    "disagree_count":poll.disagree.count(),
                    "create_date":poll.created_date,
                    

                    }
                return Response(response.values(),status=200)
            else:
                return Response(response.values(),status=200)

        elif commentId:

            poll_comment=PollComment.objects.get(id=commentId)

            try:
                profile_detail=Profile.objects.select_related('contact').get(contact__userdetail__id=poll_comment.profile.id)
            except Exception as msg:
                return Response({"message":str(msg)})
            
            response={
                    "comment_id":poll_comment.id,
                    "comment":poll_comment.comment,
                    "profile":profile_detail.profileImage.url if profile_detail.profileImage else "no image",
                    "profile_name":profile_detail.contact.profile_name,
                    "agree_count":poll_comment.agree.count(),
                    "disagree_count":poll_comment.disagree.count(),
                    "created_date":poll_comment.created_date
                    }
            return Response(response,status=200)


        elif pollid :
            
            poll_comment=PollComment.objects.select_related('poll_id').filter(poll_id__id=pollid)
            
            if poll_comment.exists():
                for poll in poll_comment:

                    profile_detail=Profile.objects.get(contact__userdetail__id=poll.profile.id)
                    
                    response[poll.id]={
                    "comment_id":poll.id,
                    "comment":poll.comment,
                    "profile":profile_detail.profileImage.url if profile_detail.profileImage else "no image",
                    "profile_name":profile_detail.contact.profile_name,
                    "agree_count":poll.agree.count(),
                    "disagree_count":poll.disagree.count(),
                    "created_date":poll.created_date
                    }
                return Response(response.values(),status=200)
            else:
                return Response(response.values(),status=200)


        else:
            return Response({"message":"some key error"},status=200)            

    def post(self,request):
        data=request.data
        pollid=get_object_or_404(Poll,id=data['poll_id'])
        userid=get_object_or_404(User,id=data['profile'])
        PollComment.objects.create(poll_id=pollid,profile=userid,comment=data['comment'])

        poll_comment=pollid.pollcomment_set.all().count()
        return Response({"message":"poll comment posted","status":"true","poll_comment":poll_comment},status=200)
    
    def put(self,request):
        commentId=request.GET.get('comment_id')
        userId=request.GET.get('user_id')
        discussionId=request.GET.get('discussion_id')
        agree_status=request.GET.get('agree')#True,False
        disagree_status=request.GET.get('disagree')#True false
        
        """OPINION FOR POLL COMMENT"""
        if commentId is not None and userId is not None:
            try:
                comment=PollComment.objects.get(id=commentId)
            except Exception as msg:
                return Response ({"message":"comment id not found","status":False},status=status.HTTP_404_NOT_FOUND)

            if agree_status is not None and disagree_status is None:
                if comment.disagree.filter(id=userId).exists():
                    comment.disagree.remove(userId)
                try:
                    comment.agree.get(id=userId)
                    comment.agree.remove(userId)
                    return Response({
                                    "agree":comment.agree.filter(id=userId).exists(),
                                    "agree_count":comment.agree.count(),
                                    "disagree":comment.disagree.filter(id=userId).exists(),
                                    "disagree_count":comment.disagree.count()
                                    })
                except Exception as msg:
                    comment.agree.add(userId)
                    return Response({
                                    "agree":comment.agree.filter(id=userId).exists(),
                                    "agree_count":comment.agree.count(),
                                    "disagree":comment.disagree.filter(id=userId).exists(),
                                    "disagree_count":comment.disagree.count(),
                    
                                    })
                

            elif disagree_status is not None and agree_status is None:
                
                if comment.agree.filter(id=userId).exists():
                    comment.agree.remove(userId)
               
                try:
                    
                    comment.disagree.get(id=userId)
                    comment.disagree.remove(userId)
                    return Response({   
                                        "agree":comment.agree.filter(id=userId).exists(),
                                        "agree_count":comment.agree.count(),
                                        "disagree":comment.disagree.filter(id=userId).exists(),
                                        "disagree_count":comment.disagree.count()
                                        
                                    })
                except Exception as msg:
                    comment.disagree.add(userId)
                    return Response({
                                        "agree":comment.agree.filter(id=userId).exists(),
                                        "agree_count":comment.agree.count(),
                                        "disagree":comment.disagree.filter(id=userId).exists(),
                                        "disagree_count":comment.disagree.count()
                                        
                                    })
            
                
                
            elif disagree_status is not None and agree_status is not None:
                return Response({"message":"your are passing to much key at same time we can't process","status":False},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"message":"Key error","status":False},status=status.HTTP_404_NOT_FOUND)

        #OPINION FOR CASE COMMENT
        elif discussionId is not None and userId is not None:
            try:
                discussion=Discussions.objects.get(id=discussionId)
            except Exception as msg:
                return Response ({"message":"comment id not found","status":False},status=status.HTTP_404_NOT_FOUND)
            
            if agree_status is not None and disagree_status is  None: 
                
                if discussion.disagree.filter(id=userId).exists():  
                    discussion.disagree.remove(userId) 
                try:
                    discussion.agree.get(id=userId)
                    discussion.agree.remove(userId)
                    return Response({   

                                        "agree":discussion.agree.filter(id=userId).exists(),
                                        "agree_count":discussion.agree.count(),
                                        "disagree":discussion.disagree.filter(id=userId).exists(),
                                        "disagree_count":discussion.disagree.count()
                                        
                                    })
                except Exception as msg:
                    discussion.agree.add(userId)
                    return Response({ 
                                        "agree":discussion.agree.filter(id=userId).exists(),
                                        "agree_count":discussion.agree.count(),
                                        "disagree":discussion.disagree.filter(id=userId).exists(),
                                        "disagree_count":discussion.disagree.count()
                                        
                                    }) 
                

            elif disagree_status is not None and agree_status is  None:
                if discussion.agree.filter(id=userId).exists():
                    discussion.agree.remove(userId)
                try:
                    discussion.disagree.get(id=userId)
                    discussion.disagree.remove(userId)
                    return Response({   
                                        "agree":discussion.agree.filter(id=userId).exists(),
                                        "agree_count":discussion.agree.count(),
                                        "disagree":discussion.disagree.filter(id=userId).exists(),
                                        "disagree_count":discussion.disagree.count()
                                    })
                except Exception as msg:
                    discussion.disagree.add(userId)
                    return Response({
                                        "agree":discussion.agree.filter(id=userId).exists(),
                                        "agree_count":discussion.agree.count(),
                                        "disagree":discussion.disagree.filter(id=userId).exists(),
                                        "disagree_count":discussion.disagree.count()
                                        
                                    })
                        
               

            elif disagree_status is not None and agree_status is not None:
                return Response({"message":"your are passing to much key at same time we can't process","status":False},status=status.HTTP_404_NOT_FOUND)

            else:
                return Response({"message":"Key error","status":False},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":"something key error","status":False},status=status.HTTP_404_NOT_FOUND)
            




"""POLL ,VOTE,COMMENT API END HERE"""






class College_Storires(APIView):
    def get(self,request):
        college_name=['Osmania Medical College','Kamineni Academy of Medical Sciences and Research Centre','Gandhi Medical College']
        response={"college_name":college_name}
       
        return Response(response,status=200)
    def post(self,request):
        data=request.data 
        if not request.POST._mutable:
            request.POST._mutable = True
        data = ast.literal_eval(request.data.get('registerdata'))
        data['photos']=request.FILES['photos']
        print(data)
        serializer=College_StorySerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"college story posted","status":True},status=200)
        return Response({"message":"errors","status":False},status=400)



""" NEWS ARTICALS POST , ARTICAL POST AND COMMENT API START HERE"""

class News_Artical_Post(APIView):
    def get(self,request):
        username_id=request.GET.get('user_id')
        newsarticalId=request.GET.get('artical_id')

        response={}
        try:
            user=User.objects.get(id=username_id)
        except Exception as e:
            return Response({"message":str(e)})
        if newsarticalId:
            query_set=Q(id=newsarticalId)
            print("if part",query_set)
        else:
            query_set=Q(created_date__date__lte=date.today())
            print("elsepart",query_set)
        newsartical=NewsArticalPost.objects.select_related('userid').filter(query_set).order_by('-created_date')
        print(newsartical)
        for artical in newsartical:
            serializer=NewsArticalPostSerializers(artical,many=False).data
            profile=Profile.objects.select_related('contact').get(contact__userdetail__id=artical.userid.id)
            
            
            response[artical.id]=serializer
           
            response[artical.id].update({
                "username":profile.contact.profile_name,
                "profileImage":profile.profileImage.url if profile.profileImage else "no image"
            })
            response[artical.id].update({
                "bookmark_status":artical.bookmark.filter(id=user.id).exists(),
                "bookmark_count":artical.bookmark.all().count(),
                "like_status":artical.likes.filter(id=user.id).exists(),
                "like_count":artical.likes.all().count(),
                "follow":profile.follow.filter(id=user.id).exists()
                
                })
        return Response(response.values(),status=200)
    
    def post(self,request):
        if not request.POST._mutable:
            request.POST._mutable = True 
        data = ast.literal_eval(request.data['registerdata'])
        data['artical_image']=request.FILES['artical_image']
        serializer=NewsArticalPostSerializers(data=data)
        print(data) 
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"news artical posted","status":True},status=200)
        return Response({"message":"errors","status":False},status=400)

"""ARTICAL GET AND POST """
class ArticalPost(APIView):
    def get(self,request):
        response={}
        articalid=request.GET.get('artical_id')
       
        if articalid:
            try:
                artical_author=Articals.objects.get(id=articalid)
            except Exception as msg:
                return Response({"message":str(msg)})
            try:
                profile_detail=Profile.objects.get(contact__userdetail__id=artical_author.user.id)
            except Exception as msg:
                return Response({"message":str(msg)})
            
        
        
            artical_comment=artical_author.articalcomment_set.all()
            
           
            for artical in artical_comment:
                comment_profile=Profile.objects.get(contact__userdetail__id=artical.profile.id)
                response[artical.id]={
                "comment_id":artical.id,
                "comment":artical.comment,
                "profile":comment_profile.profileImage.url if comment_profile.profileImage else "no image",
                "profile_name":comment_profile.contact.profile_name,
                "location":comment_profile.contact.current_job_location,
                "speciality":comment_profile.contact.speciality,
                "create_date":artical.created_date

                }
            serializers=ArticalsSerializers(artical_author,many=False).data
            serializers.update({
                                "profile_name":profile_detail.contact.profile_name,
                                "profileImage":profile_detail.profileImage.url if profile_detail.profileImage else "no image",
                                "location":profile_detail.contact.current_job_location,
                                "speciality":profile_detail.contact.speciality,
                                })
            serializers.update({"artical_comment":response.values()})
            return Response(serializers,status=200)

        


        else:
            return Response({"message":"some key error"},status=200)    

    def post(self,request):
        data=request.data 
        if not request.POST._mutable:
            request.POST._mutable = True
        data = ast.literal_eval(request.data.get('registerdata'))
        data['mediafile']=request.FILES['mediafile']
        print(data)
        serializer=ArticalsSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Artical posted","status":True},status=200)
        return Response({"message":"errors","status":False},status=400)


"""ARTICAL COMMENTS"""
class Artical_Comment(APIView):

    def get(self,request):
        response={}
        articalid=request.GET.get('artical_id')
        username_id=request.GET.get('user_id')
        commentId=request.GET.get('comment_id')

        
        if articalid and username_id:
            try:
                profile_detail=Profile.objects.get(contact__userdetail__id=username_id)
            except Exception as msg:
                return Response({"message":str(msg)})
            artical_comment=ArticalComment.objects.select_related('artical_id','profile').filter(artical_id__id=articalid,profile__id=username_id)
            
            if artical_comment.exists():
                for artical in artical_comment:
                    response[artical.id]={
                    "comment_id":artical.id,
                    "comment":artical.comment,
                    "profile":profile_detail.profileImage.url if profile_detail.profileImage else "no image",
                    "profile_name":profile_detail.contact.profile_name,
                    "create_date":artical.created_date,

                    }
                return Response(response.values(),status=200)

        elif commentId:

            artical_comment=ArticalComment.objects.get(id=commentId)

            try:
                profile_detail=Profile.objects.select_related('contact').get(contact__userdetail__id=artical_comment.profile.id)
            except Exception as msg:
                return Response({"message":str(msg)})
            
            response={
                    "comment_id":artical_comment.id,
                    "comment":artical_comment.comment,
                    "profile":profile_detail.profileImage.url if profile_detail.profileImage else "no image",

                    "profile_name":profile_detail.contact.profile_name,
                    "create_date":artical_comment.created_date,
                    }
            return Response(response,status=200)


        elif articalid:
            
            artical_comment=ArticalComment.objects.select_related('artical_id').filter(artical_id__id=articalid)
            
            if artical_comment.exists():
                for artical in artical_comment:

                    profile_detail=Profile.objects.get(contact__userdetail__id=artical.profile.id)
                    
                    response[artical.id]={
                    "comment_id":artical.id,
                    "comment":artical.comment,
                    "profile":profile_detail.profileImage.url if profile_detail.profileImage else "no image",
                    "profile_name":profile_detail.contact.profile_name,
                    "create_date":artical.created_date,

                    }
                return Response(response.values(),status=200)
            else:
                return Response(response.values(),status=400)


        else:
            return Response({"message":"some key error"},status=200)            

    def post(self,request):
        data=request.data
        articalid=get_object_or_404(Articals,id=data['artical_id'])
        userid=get_object_or_404(User,id=data['profile'])
        ArticalComment.objects.create(artical_id=articalid,profile=userid,comment=data['comment'])

        artical_comment=articalid.articalcomment_set.all().count()
        return Response({"message":"artical comment posted","status":"true","artical_comment":artical_comment},status=200)

""" NEW ARTICAL POST ,ARTICAL POST AND COMMENT API END """




"""COMPLAINT POST AND COMMENT API START"""
class Complaint_Post(APIView):
    def get(self,request):
        
        single_complaint=request.GET.get('complaint_id')
        if single_complaint:
            comp=Complaint.objects.get(id=single_complaint)
            serializer=ComplaintSerializers(comp,many=False).data
            profile=Profile.objects.get(contact__userdetail__id=comp.complaint_id.id)
            serializer1={
                        "ProfileName":profile.contact.profile_name,
                        "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
                        "speciality":profile.contact.speciality,
                        "location":profile.contact.current_job_location
                        }
            serializer.update(serializer1)
            
            return Response(serializer,status=200)
        comp=Complaint.objects.all()
        return Response(ComplaintSerializers(comp,many=True).data ,status=200)
        
    def post(self,request):
        if not request.POST._mutable:
            request.POST._mutable = True
        data = ast.literal_eval(request.data['registerdata'])
        print(data)
        #data=request.data
        try:
            user=User.objects.get(id=data['complaint_id'])
        except Exception as e:
            return Response({"message":str(e)})
        data['com_image']=request.FILES['com_image']
        print(data)
        serializer=ComplaintSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=400)
    


class Complaint_Comment(APIView):

    def get(self,request):
        response={}
        caseid=request.GET.get('complaint_id')
        username_id=request.GET.get('user_id')
        commentId=request.GET.get('comment_id')

        
        if caseid and username_id:
            total_discussion=Discussions.objects.select_related('case_id','profile').filter(case_id__id=caseid,profile__id=username_id)
            try:
                profile_detail=Profile.objects.get(contact__userdetail__id=username_id)
            except Exception as msg:
                return Response({"message":str(msg)})
            if total_discussion.exists():
                for dis in total_discussion:
                    response[dis.id]={
                    "comment_id":dis.id,
                    "comment":dis.comment,
                    "profile":profile_detail.profileImage.url if profile_detail.profileImage else "no image",
                    "profile_name":profile_detail.contact.profile_name,
                    "agree":dis.agree.filter(id=username_id).exists(),
                    "disagree":dis.disagree.filter(id=username_id).exists(),
                    "agree_count":dis.agree.count(),
                    "disagree_count":dis.disagree.count(),
                    "create_date":dis.created_date,


                    }
                return Response(response.values(),status=200)

        elif commentId:
            discussion=Discussions.objects.get(id=commentId)
            profile_detail=Profile.objects.get(contact__userdetail__id=discussion.profile.id)
            response={
                    "comment_id":discussion.id,
                    "comment":discussion.comment,
                    "profile":profile_detail.profileImage.url if profile_detail.profileImage else "no image",
                    "profile_name":profile_detail.contact.profile_name,
                    "create_date":discussion.created_date,
                    "agree_count":discussion.agree.count(),
                    "disagree_count":discussion.disagree.count(),


                    }
            return Response(response,status=200)


        elif caseid:
            total_discussion=Discussions.objects.select_related('case_id').filter(case_id__id=caseid)
            
            if total_discussion.exists():
                for dis in total_discussion:
                    profile_detail=Profile.objects.get(contact__userdetail__id=dis.profile.id)
                    response[dis.id]={
                    "comment_id":dis.id,
                    "comment":dis.comment,
                    "profile":profile_detail.profileImage.url if profile_detail.profileImage else "no image",
                    "profile_name":profile_detail.contact.profile_name,
                    "create_date":dis.created_date,
                    "agree_count":dis.agree.count(),
                    "disagree_count":dis.disagree.count(),
                    

                    }
                return Response(response.values(),status=200)


        else:
            return Response({"message":"some key error"},status=200)


    def post(self,request):
        data=request.data
        complaintid=get_object_or_404(Complaint,id=data['case_id'])
        userid=get_object_or_404(User,id=data['profile'])
        Discussions.objects.create(case_id=complaintid,profile=userid,comment=data['comment'])
        total_discussion=complaintid.discussions_set.all().count()
        return Response({"message":"artical comment posted","status":"true","discussion":total_discussion},status=200)

"""COMPLAINT POST AND COMMENT API END"""




""""THIS IS FOR HOME PAGE API IT HAS COMPLAINT,POLL,ARTICAL THIS IS BASE ON CREATED DATE"""
"""news/poll/complaint/"""
class ComplaintAndPoll(APIView):
    def get(self,request):
        response={}

        username_id=request.GET.get('user_id')

        polls=Poll.objects.values('created_date')

        complaints=Complaint.objects.values('created_date')

        NewArtical=Articals.objects.values('created_date')

        three_table_join=polls.union(complaints,NewArtical).order_by('-created_date')
       
        
        
        user=get_object_or_404(User,id=username_id)
        
        
        
        for i in range(len(three_table_join)):
            sortedpolls=Poll.objects.filter(created_date=three_table_join[i]['created_date'])
            
           
            for poll in sortedpolls:
                
                

                serializer=PollSerializers(poll,many=False).data
                poll_pro=Profile.objects.select_related('contact').get(contact__userdetail__id=poll.poll_user.id)
                
                poll_profile={  
                                "userid":poll.poll_user.id,
                                "ProfileName":poll_pro.contact.profile_name,
                                "ProfileImage":poll_pro.profileImage.url if poll_pro.profileImage else "no image",
                                "speciality":poll_pro.contact.speciality,
                                "location":poll_pro.contact.current_job_location
                            }
                serializer.update(poll_profile)
                
                find_existing_voter_or_not=PollVote.objects.select_related('poll_id','profile').filter(poll_id__id=poll.id,profile__id=user.id)
                

                collect_total_vote=poll.pollvote_set.count()
    
                choiceA=poll.pollvote_set.filter(choice="A").count()
                try:    
                    choiceA_percentage=int((choiceA/collect_total_vote)*100) 
                except ZeroDivisionError:
                    choiceA_percentage=choiceA
                
                choiceB=poll.pollvote_set.filter(choice="B").count()
                try:
                    choiceB_percentage=int((choiceB/collect_total_vote)*100)
                except ZeroDivisionError:
                    choiceB_percentage=choiceB 

                choiceC=poll.pollvote_set.filter(choice="C").count()
                try:
                    choiceC_percentage=int((choiceC/collect_total_vote)*100) 
                except ZeroDivisionError:
                    choiceC_percentage=choiceC
                
                choiceD=poll.pollvote_set.filter(choice="D").count()
                try:
                    choiceD_percentage=int((choiceD/collect_total_vote)*100) 
                except ZeroDivisionError:
                   choiceD_percentage=choiceD

                if user.id != poll_pro.contact.userdetail.id:
                    follow=poll_pro.follow.filter(id=user.id).exists()
                else:
                    follow="uploader"
                

                like=poll.likes.filter(id=user.id)

                poll_comment=PollComment.objects.select_related('poll_id','profile').filter(poll_id__id=poll.id)

                comment={}
                for pollcom in poll_comment:
                    profile_detail=Profile.objects.get(contact__userdetail__id=pollcom.profile.id)
                    comment[pollcom.id]={
                    "userid":pollcom.profile.id,
                    "comment_id":pollcom.id,
                    "comment":pollcom.comment,
                    "ProfileName":profile_detail.contact.profile_name,
                    "ProfileImage":profile_detail.profileImage.url if profile_detail.profileImage else "no image"

                    }
                serializer.update({"comment":comment.values()}) 

                bookmark=poll.bookmark.filter(id=user.id)
                serializer.update({
                                "bookmark_status":bookmark.exists(),
                                "bookmark_count":poll.bookmark.all().count(),
                                "like_status":like.exists(),
                                "like_count":poll.likes.all().count(),
                                "follow":str(follow),
                                "complaint_status":False,
                                "art_status":False,
                                "votes":poll.pollvote_set.count(),
                                "likes":poll.likes.all().count(),
                                "user_status":find_existing_voter_or_not.exists(),
                                "A":choiceA_percentage,
                                "B":choiceB_percentage,
                                "C":choiceC_percentage,
                                "D":choiceD_percentage,
                                "choice":find_existing_voter_or_not[0].choice if find_existing_voter_or_not.exists() else "no_opinion" ,
                                "discussion":poll_comment.count()
                   
                                })
                
                response[random.randint(1,9999)]=serializer


            complaints=Complaint.objects.filter(created_date=three_table_join[i]['created_date'])
           
            for complaint in complaints:
                serializer1=ComplaintSerializers(complaint,many=False).data
                complaint_profile=Profile.objects.select_related('contact').get(contact__userdetail__id=complaint.complaint_id.id)
                case_profile={
                            "userid":complaint.complaint_id.id,
                            "ProfileName":complaint_profile.contact.profile_name,
                            "ProfileImage":complaint_profile.profileImage.url if complaint_profile.profileImage else "no image",
                            "speciality":complaint_profile.contact.speciality,
                            "location":complaint_profile.contact.current_job_location
                            }
                
                serializer1.update(case_profile)

                discussion=Discussions.objects.select_related('case_id','profile').filter(case_id__id=complaint.id)

                comment={}
                for dis in discussion:
                    profile_detail=Profile.objects.get(contact__userdetail__id=dis.profile.id)
                    comment[dis.id]={
                    "userid":dis.profile.id,
                    "comment_id":dis.id,
                    "comment":dis.comment,
                    "ProfileName":profile_detail.contact.profile_name,
                    "ProfileImage":profile_detail.profileImage.url if profile_detail.profileImage else "no image"

                    }
                serializer1.update({"comment":comment.values()}) 
                if user.id != complaint_profile.contact.userdetail.id:
                    follow=complaint_profile.follow.filter(id=user.id).exists()
                else:
                    follow="uploader"
                #follow=complaint_profile.follow.filter(id=user.id)
                like=complaint.likes.filter(id=user.id)
                bookmark=complaint.bookmark.filter(id=user.id)
                serializer1.update({
                                "bookmark_status":bookmark.exists(),
                                "bookmark_count":complaint.bookmark.all().count(),
                                "like_status":like.exists(),
                                "like_count":complaint.likes.all().count(),
                                "follow":str(follow),
                                "poll_status":False,
                                "art_status":False ,
                                "discussion":discussion.count()
                   
                                })
                response[random.randint(1,9999)]=serializer1

            NewArtical=Articals.objects.filter(created_date=three_table_join[i]['created_date'])
            for artical in NewArtical:
                serializer2=ArticalsSerializers(artical,many=False).data
               
                artical_profile=Profile.objects.get(contact__userdetail__id=artical.user.id)
                case_profile={
                                "userid":artical.user.id,
                                "ProfileName":artical_profile.contact.profile_name,
                                "ProfileImage":artical_profile.profileImage.url if artical_profile.profileImage else "no image",
                                "speciality":artical_profile.contact.speciality,
                                "location":artical_profile.contact.current_job_location
                            }
                serializer2.update(case_profile)

                artical_comment=ArticalComment.objects.select_related('artical_id','profile').filter(artical_id__id=artical.id)
                art_comment={}
                for art in artical_comment:
                    profile_detail=Profile.objects.get(contact__userdetail__id=art.profile.id)
                    art_comment[art.id]={
                    "userid":art.profile.id,
                    "comment_id":art.id,
                    "comment":art.comment,
                    "ProfileName":profile_detail.contact.profile_name,
                    "ProfileImage":profile_detail.profileImage.url if profile_detail.profileImage else "no image",
                    "speciality":profile_detail.contact.speciality

                    }
                serializer2.update({"comment":art_comment.values()}) 

                if user.id != artical_profile.contact.userdetail.id:
                    follow=artical_profile.follow.filter(id=user.id).exists()
                else:
                    follow="uploader"

                artical_comment=artical.articalcomment_set.all().count()
                #follow=artical_profile.follow.filter(id=user.id)
                like=artical.likes.filter(id=user.id)
                bookmark=artical.bookmark.filter(id=user.id)
                serializer2.update({
                                "bookmark_status":bookmark.exists(),
                                "bookmark_count":artical.bookmark.all().count(),
                                "like_status":like.exists(),
                                "like_count":artical.likes.all().count(),
                                "follow":str(follow),
                                "poll_status":False,
                                "complaint_status":False,
                                "artical_comment":artical_comment
                   
                                })
                response[random.randint(1,9999)]=serializer2

            

        
        return Response(response.values())



            
           

class JobRequestPost(APIView):
    def get(self,request):
        
        location=[ loc.hospital_city_name for loc in City.objects.all()]
        response={
                "hospital_type":[type.hospitaltype for type in Hospital_Type.objects.exclude(position="Others")],
                "position":[pos.position  for pos in Designation.objects.all()],
                "department":[dep.department_name for dep in Hospital_Department.objects.all()],
                "salary":[s for s in range(30000,70000,5000)],
                "location":location,
                "vacancy":[i for i in range(1,10)],
                "job_type":['Full_Time','Part_Time']

            }
        
        return Response(response,status=200)

    def post(self,request):
        if not request.POST._mutable:
            request.POST._mutable = True
        data=request.data 
        print(data)
        serializer=RequestJobPostSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"job posted"})
        return Response(serializers.errors,status=404)



"""CUSTOM JOBS GET HERE"""
class User_Customize_Jobs(APIView):
    def get(self,request):
        related_job=request.GET.get('userid')
        username_id=request.GET.get('user_id')
 
        if related_job or username_id:
            resp={}

            if username_id:
                query_set=Q(id=username_id)
                job_query_set=Q(user_id__id=username_id)
            
            elif related_job:
                query_set=Q(id=related_job)
                job_query_set=Q(user_id__id=related_job)
            
            try:
                user=User.objects.get(query_set)
                
            except Exception as e:
               
                return Response(resp.values(),status=200)

            try:
                
                job=Custome_Job.objects.get(job_query_set)
                category_job=Category_Related_Job.objects.filter(
                                    Q(
                                        department__iexact=job.department,designation__iexact=job.job_position,
                                        hospital_type__iexact=job.type_of_hospital,job_type__iexact =job.jobType,
                                        salary=job.minimum_salary,location__iexact=job.location,
                                        accommodation__iexact=job.allowance,experince__iexact=job.work_expericence,
                                    )
                        
                            )
                job_status=True
            except Exception as e:
                job_status=False
                pass
               
            if username_id:
               

                resp={
                    "total_custome_job":category_job.count() if job_status else 0,
                    "save_jobs":Category_Related_Job.objects.filter(bookmark=user).count(),
                    "apply_job":Category_Related_Job.objects.filter(applicant=user).count(),
                    "interview_call":Category_Related_Job.objects.filter(job_status=True).count(),
                
                }
                return Response(resp,status=200)
            
            elif related_job:
                if job_status:
                    for category in category_job:
                        serilaizer=Category_Related_JobSerializers(category,many=False)
                        resp[category.id]=serilaizer.data
                        resp[category.id].update({
                            "bookmark_status":category.bookmark.filter(id=user.id).exists(),
                            "like_status":category.likes.filter(id=user.id).exists(), 
                            "apply_status":category.applicant.filter(id=user.id).exists(),
                                                })
                        
                    return Response(resp.values(),status=200)
                else:
                    return Response(resp.values(),status=200)

        else:
            response={
                "department":[dep.department_name for dep in Hospital_Department.objects.all()],
                "postion_of_job":[pos.position for pos in Designation.objects.all()], 
                "type_of_hospital":[type.hospitaltype for type in Hospital_Type.objects.all()], 
                "city_of_hospital":[cat['location']  for cat in Category_Related_Job.objects.values('location').distinct()],
                "minimum_salary":[salary.min_salary for salary in Salary.objects.all()] ,   
                "work_experince":[experince for experince in range(1,10)], 
                "job_type":["Part_Time","Full_Time"], 
                "accommodation":["Yes","No"]
            }
            
            return Response(response,status=200)
    
    def post(self,request):
        data=request.data 
        try:
            custom_job=get_object_or_404(Custome_Job,user_id__id=data['user_id'])
            serializer=Custome_JobSerializers(custom_job,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=200)
            return Response(serializer.errors,status=400)
            
        except Exception as e:
            get_object_or_404(User,id=data['user_id'])
            serializer=Custome_JobSerializers(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=200)
            return Response(serializer.errors,status=400)
    


#MultiImage 
class Multi_Image_Post(APIView):
    def post(self,request):
        if not request.POST._mutable:
            request.POST._mutable = True
        
        complaintId=request.GET.get('complaint_id')
        pollId=request.GET.get('poll_id')
        multiple_image=request.FILES.getlist('multi_image')
        data = ast.literal_eval(request.data.get('registerdata'))
        if complaintId:
            complaint=get_object_or_404(Complaint,id=complaintId)
            for img in multiple_image:
            
                MultiImage.objects.create(complaint=complaint,image=img,complaint_status=True)

            return Response({"message":"multiple_image post for news articals","status":True},status=200)
        elif pollId:
            poll=get_object_or_404(Poll,id=pollId)
            for img in multiple_image:
            
                MultiImage.objects.create(news_poll=poll,image=img,newspoll_status=True)

            return Response({"message":"multiple_image post for news articals","status":True},status=200)
        return Response({"message":"key error","status":False},status=400)


class Job_Banner(APIView):
    def get(self,request):

        bannerid=request.GET.get('bannerid')
        banner=Banner.objects.all()
        if bannerid:
            return Response(BannerSerializers(banner.get(id=bannerid),many=False).data,status=status.HTTP_200_OK)

        return Response(BannerSerializers(banner,many=True).data,status=status.HTTP_200_OK)


class Promotional_Banner(APIView):
    def get(self,request):

        bannerid=request.GET.get('bannerid')
        banner=HomeBanner.objects.all()
        if bannerid:
            return Response(HomeBannerSerializers(banner.get(id=bannerid),many=False).data,status=status.HTTP_200_OK)

        return Response(HomeBannerSerializers(banner,many=True).data,status=status.HTTP_200_OK)



"""THIS IS FOR UPLOAD STATUS,USER MULTIPLE PHOTO AND VIDEOS"""
class Upload_status(APIView):
    def post(self,request):
        if not request.POST._mutable:
            request.POST._mutable = True
        
        profileid=request.GET.get('user_id')
        multiple_image=request.FILES.getlist('multi_image')
        
        if profileid:
            user=get_object_or_404(User,id=profileid)
            profile=get_object_or_404(Profile,contact__userdetail__id=user.id)
           
            for img in multiple_image:
                
            
                MultiImageStatus.objects.create(profile=profile,image=img)

            return Response({"message":"successfully uploaded image","status":"true"},status=200)
        
        else:
            return Response({"message":"key error","status":False},status=400) 

    def get(self,request):
        response={}
        profileid=request.GET.get('user_id')
        show_all_status=request.GET.get('userid')
        what_my_status=request.GET.get('my_status')
        
        
        try:
            user=User.objects.get(Q(id=profileid) | Q(id=show_all_status) | Q(id=what_my_status))
        except ObjectDoesNotExist:
            return Response({"message":"user id not exits"},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            profile=Profile.objects.get(contact__userdetail__id=user.id)
        except ObjectDoesNotExist:
            return Response({"message":"profile id not exits"},status=status.HTTP_400_BAD_REQUEST)

        if profileid:
            
            multiple_image=profile.multiimagestatus_set.all() 
            for img in multiple_image:
                response[img.id]={
                "id":img.id,
                "image":img.image.url if  img.image else "no status"
                }
            return Response(response.values())
        
        elif what_my_status:
            multiple_image=profile.multiimagestatus_set.all() 
            return Response({"story_status":multiple_image.exists(),
                            "id":user.id,
                            "image":profile.profileImage.url if profile.profileImage else "no image"
                            })

        elif show_all_status:
            multiple_image=MultiImageStatus.objects.select_related('profile').filter(~Q(profile__id=profile.id)).order_by('-created')
            for i in multiple_image:
                calculated_time=datetime.now() - i.created
                tatal_sec_in_one_day=(24*60*60)
                if tatal_sec_in_one_day >= calculated_time.total_seconds():
                    
                    response[i.profile.id]={
                        "id":i.profile.contact.userdetail.id,
                        "name":i.profile.profile_name,
                        "image":i.profile.profileImage.url if i.profile.profileImage else "no image"    
                    }
                else:
                    i.delete()
                    pass
                
          
            return Response(response.values())

""" ########################JOB SEARCH API START ##########################"""

"""SPECILITIES SEARCH"""





class Hospital_Type_Lists(APIView):
    def get(self,request):
        HT= Hospital_Type.objects.exclude(position="Others")
        serializers=HospitalTypeSerializer(HT,many=True)
        return Response(serializers.data)



class SearchResult(APIView):
    def get(self,request,*args,**kwargs):
        resp={}
        get_value=request.query_params
        category=get_object_or_404(Job_By_Category,id=get_value['category_id'])
       
        user_filter_query=[Q(category=category.id)]
        user=get_object_or_404(User,id=request.query_params['user_id'])
        print(get_value)
        
        for data in get_value:
            if "location" == data:
                query=Q(location__in=get_value['location'].split(","))
                user_filter_query.append(query)
                print(query)
                print(user_filter_query)
                

               
            
            elif "specialist" == data:
                query=Q(course__in=get_value['specialist'].split(","))
                user_filter_query.append(query)
                print(query)
                print(user_filter_query)
               
            elif "super_specialist" == data:
                query=Q(course__in=get_value['super_specialist'].split(","))
                user_filter_query.append(query)
                print(query)
                print(user_filter_query)
                
                
            elif "position" == data:
                query=Q(designation__in=get_value['position'].split(","))
                user_filter_query.append(query)
                print(query)
                print(user_filter_query)
               
            elif "graduation" == data:
                query=Q(qualification__in=get_value['graduation'].split(","))
                user_filter_query.append(query)
                print(query)
                print(user_filter_query)
                
               
            
        new_job=Category_Related_Job.objects.select_related('category').filter(reduce(operator.and_, user_filter_query)).order_by('-created_date')
        print(new_job) 
        for categorys in new_job:
            print(categorys)
            
            
            serializer=Category_Related_JobSerializers(categorys,many=False).data
            resp[categorys.id]=serializer
            
            resp[categorys.id].update({
                    
                        "bookmark_status":categorys.bookmark.filter(id=user.id).exists(),
                        "like_status":categorys.likes.filter(id=user.id).exists(), 
                        "apply_status":categorys.applicant.filter(id=user.id).exists(),
                                    })
            
        return Response(resp.values(),status=200)
       

'''api/job/loction/'''
'''job search by location'''
class Location_By_job_search(APIView):
    def get(self,request,format=None):
        locationId=request.GET.get('location')
        username_id=request.GET.get('user_id')
        statename=request.GET.get('state')
        course=request.GET.get('course').split(",") if request.GET.get('course') is not None else request.GET.get('course')
        resp={}
        if locationId:
           
            user=get_object_or_404(User,id=username_id)
            
            
            if locationId and course:
                user_query=Q(location=locationId,course__in=course)  
            
            elif locationId:
                user_query=Q(location=locationId)
                
            job_category=Category_Related_Job.objects.filter(user_query).order_by('-created_date')
            
            for category in job_category:
                
                serializer=Category_Related_JobSerializers(category,many=False).data
                resp[category.id]=serializer
                
                resp[category.id].update({
                        "bookmark_status":category.bookmark.filter(id=user.id).exists(),
                        "like_status":category.likes.filter(id=user.id).exists(), 
                        "apply_status":category.applicant.filter(id=user.id).exists(),
                            })
                
            return Response(resp.values(),status=200)
        elif statename is not None:
            state=get_object_or_404(State,name=statename)
            cities=state.city_set.all()
            for city in cities:
                resp[city.id]={
                    "id":city.id,
                    "location":city.hospital_city_name,
                        }
            
            return Response(resp.values(),status=200)

            
        else:
            for city in City.objects.all():
                resp[city.id]={
                    "id":city.id,
                    "location":city.hospital_city_name,
                        }
            
            return Response(resp.values(),status=200)


"""JOB SEARCH BY DEPARTMENT"""
"""api/job/department/"""
class Department_By_Job(APIView):
    def get(self,request):
        departmental_job=request.GET.get('department')
        location=request.GET.get('location').split(",") if request.GET.get('location') is not None else request.GET.get('location')
        username_id=request.GET.get('user_id')
        response={}
        if departmental_job:

            if departmental_job and location:
                user_query=Q(department=departmental_job,location__in=location)
            elif departmental_job:
                user_query=Q(department__iexact=departmental_job)
            
            user=get_object_or_404(User,id=username_id)
               
            job_by_location=Category_Related_Job.objects.filter(user_query).order_by('-created_date')
            
            for category in job_by_location:
                serializer=Category_Related_JobSerializers(category,many=False).data
                response[category.id]=serializer
                response[category.id].update({
                        "bookmark_status":category.bookmark.filter(id=user.id).exists(),
                        "like_status":category.likes.filter(id=user.id).exists(), 
                        "apply_status":category.applicant.filter(id=user.id).exists(),
                            })

            
            return Response(response.values(),status=200)
        

        else:
            departments=Hospital_Department.objects.all()
            
            for department in departments:
            
              
                response[department.id]={
                    "id":department.id,
                    "department":department.department_name
                    
                }
            return Response(response.values(),status=200)


"""JOB SEARCH BY LOCATION DEPARTMENT DESIGNATION"""

class Search_Location_Department_Designation(APIView):
    def get(self,request,format=None):
        resp={}
        multi_location_input=request.GET.get('location').split(",")
       
        
        
        multi_department_input=request.GET.get('department').split(",") 
       
        multi_designation_input=request.GET.get('designation').split(",") 
        
        

        username_id=request.GET.get('user_id')
        """USER FIND"""
        user=get_object_or_404(User,id=username_id)
        
        """USER QUERY """
        
     
        if (len(multi_location_input[0])>=2) and (len(multi_department_input[0])>=2) and (len(multi_designation_input[0])>=2):
            user_query=Q(
                            Q(
                                location__in=multi_location_input,
                                Speciality__in=multi_department_input,
                                designation__in=multi_designation_input
                        )

            )
            print("3",user_query)
        elif (len(multi_location_input[0])>=2) and (len(multi_department_input[0])>=2) :
            user_query=Q(
                            Q(
                                location__in=multi_location_input,
                                Speciality__in=multi_department_input,
                           
                            )

                    )
            print("2",user_query)
        elif (len(multi_location_input[0])>=2) and (len(multi_designation_input[0])>=2) :
            user_query=Q(
                            Q(
                                location__in=multi_location_input,
                                designation__in=multi_designation_input,
                            
                            )

                    )
            print("2",user_query)
        elif (len(multi_department_input[0])>=2) and (len(multi_designation_input[0])>=2) :
            user_query=Q(
                            Q(
                                Speciality__in=multi_department_input,
                                designation__in=multi_designation_input,
                            
                            )

                    )
            print("2",user_query)
        elif multi_location_input or multi_department_input or multi_designation_input:
            user_query=Q(
                           
                                Q(location__in=multi_location_input)
                                |
                                Q(Speciality__in=multi_department_input)
                                |
                                Q(designation__in=multi_designation_input)
                       

                        )
            print("1",user_query)
        data={  
                "id":username_id,
                "location": ",".join(multi_location_input),
                "department":",".join(multi_department_input),
                "disignation":",".join(multi_designation_input),
            }
            
        RecentSearch.objects.update_or_create(user=user,search=data)    
        """GETING JOBS HERE BASED ON USER QUERY"""
        number_of_jobs_search_releate=Category_Related_Job.objects.filter(user_query,job_status=True).order_by('-created_date')
        print(number_of_jobs_search_releate)
        """GETING SINGLE JOB AND BINDING BOOKMARK,LIKE,APPLY"""           
        for jobs in number_of_jobs_search_releate:


            status_data={
                        "bookmark_status":jobs.bookmark.filter(id=user.id).exists(),
                        "like_status":jobs.likes.filter(id=user.id).exists(), 
                        "apply_status":jobs.applicant.filter(id=user.id).exists(),
                        }
            
            serializer=Category_Related_JobSerializers(jobs,many=False).data
            serializer.update(status_data)
            resp[jobs.id]=serializer  
        return Response(resp.values(),status=200)
        

class Recent_Search(APIView):
    def get(self,request,format=None):
        
        user=get_object_or_404(User,id=request.GET.get('user_id'))  
        result=RecentSearch.objects.filter(user=user).order_by("-created")[:10]
        serializer=RecentSearchSerializer(result,many=True) 
        return Response(serializer.data,status=200)
            


class All_Jobs(APIView):
    def get(self,request):
        category=request.GET.get('catid')
        resp={}
        if category:
            new_job=Category_Related_Job.objects.filter(category__id=category).order_by('-created_date')
            print("particular category by jobs")
        else:
            new_job=Category_Related_Job.objects.all().order_by('-created_date')
            print("all category jobs")

        print(new_job) 
        user=get_object_or_404(User,id=request.query_params['user_id'])
        for categorys in new_job:
            print(categorys)
            
            
            serializer=Category_Related_JobSerializers(categorys,many=False).data
            resp[categorys.id]=serializer
            
            resp[categorys.id].update({
                        "category_id":categorys.category.id,
                        "category_name":categorys.category.title,
                        "bookmark_status":categorys.bookmark.filter(id=user.id).exists(),
                        "like_status":categorys.likes.filter(id=user.id).exists(), 
                        "apply_status":categorys.applicant.filter(id=user.id).exists(),
                                    })
            
        return Response(resp,status=200)
        #return Response(resp.values(),status=200)


"""END JOB SEARCH API"""


