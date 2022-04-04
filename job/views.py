
from django.http import response
from django.shortcuts import render,get_object_or_404

from rest_framework.response import Response 
from rest_framework.parsers import FormParser,MultiPartParser,JSONParser 
from rest_framework import status
from django.core.paginator import Paginator
from .models import *
from .send_otp import *
from django.db.models import Q
from rest_framework.views import APIView
from .serializers import *
from django.contrib.auth.models import User
import random
from django.contrib.auth import authenticate,login,logout
import ast
from datetime import *
from django.db.models import Count
from functools import partial, reduce
from rest_framework.parsers import FileUploadParser
from AdminUser.models import Question,AtteptQuestion
from AdminUser.serializers import HospitalInfoSerializers, QuestionSerializers,AtteptQuestionSerializers,HospitalBanner
from listdata.collegedata import *
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
                return Response({'message':"authorized user","Verified":identification.status,"status":identification.status},status=status.HTTP_200_OK)

            elif identification.status==True:
                if get_otp_status:
                    sending_otp(get_otp_from_database.otp,phone)
                else:
                    SaveOtp.objects.create(phone_number=phone,otp=generated_otp)
                    sending_otp(generated_otp,phone)
                return Response({ 'message':"Otp sented Successful","Verified":identification.status,"status":identification.status},status=status.HTTP_200_OK)
            else:
               
                sending_otp(get_otp_from_database.otp,phone)
                print("sec time otp")
                return Response({'message':"authorized user","Verified":identification.status,"status":identification.status},status=status.HTTP_200_OK)
        
        except Exception as msg:
           
            
            random_generated_number=random.randint(10000,99999)
            
            try:
                user=User.objects.create_user(
                                            username=data['profile_name']+"@job"+str(random_generated_number),
                                            email=data['email'],
                                        )
            except Exception as msg:
                return Response({"message":str(msg),"status":False,"Verified":False,},status=status.HTTP_400_BAD_REQUEST)
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
                user.delete()

                return Response({"message":str(msg),"status":False,"Verified":False,},status=status.HTTP_400_BAD_REQUEST)
            try:
                SaveOtp.objects.create(phone_number=phone,otp=generated_otp)
               
            except Exception as msg:
                return Response({"message":str(msg),"status":False})
            try:
                sending_otp(generated_otp,phone)
            except Exception as msg:
                return Response({"message":str(msg),"status":False})

            return Response({'message':"Otp sented Successful","registration":"registration complited","Verified":reg_pro.status,"status":reg_pro.status},status=status.HTTP_200_OK)
        

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
            contact=Identification.objects.get(phone_number=data['phone_number'])
        except Exception as msg:
            return Response({"message":"this phone is not a register try first registration","status":False},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            get_otp_from_database=SaveOtp.objects.get(phone_number=contact.phone_number)
            get_otp_status=True
        except Exception as msg:
            SaveOtp.objects.create(phone_number=contact.phone_number,otp=generated_otp)
            get_otp_status=False
            pass
        
      
        if get_otp_status:
            sending_otp(get_otp_from_database.otp,contact.phone_number)
        else:
            sending_otp(generated_otp,contact.phone_number)

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
        """GETTING PROFILE FOR GENDER DOB"""
        profile=get_object_or_404(Profile,contact=contact)
        
        if data.get('dob'):
            profile.dob=data.get('dob')
            profile.save()
        if data.get('gender'):
            profile.gender=data.get('gender')
            profile.save()
            
        
        serializers=IdentificationSerializers(contact,data=data,partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response({"message":"update successfull","status":True},status=201)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)

            

"""HERE PROFILE RELETED ALL DETAIL  AND PROFESSION RELATED DATA HERE  GET POST PUT  PATCH"""
"""api/job/profile"""
class User_Profile(APIView):
    def get(self,request,format=None):
        username_id=request.GET.get('user_id')
        requestedprofile=request.GET.get('requested_user_id')
        if username_id is not None and requestedprofile is None:
            query=Q(id=username_id)
        elif username_id is not None and requestedprofile is not None:
            query=Q(id=requestedprofile)
        user=get_object_or_404(User,query)
        contact=user.identification_set.get(userdetail=user)
        profile=Profile.objects.get(contact=contact)

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
        
        
       
        
        
        if username_id is not None and requestedprofile is  None:
            status_data={
                "bookmark_status":Category_Related_Job.objects.filter(bookmark__id=user.id).count(),
                "jobs_like":Category_Related_Job.objects.filter(likes__id=user.id).count(),
                "follow":profile.follow.filter(id=user.id).count(),
                "followStatus":profile.follow.filter(id=user.id).exists(),
                "following":Profile.objects.filter(follow=profile.contact.userdetail).count(),
                "applied_jobs":Category_Related_Job.objects.filter(applicant=user.id).count() ,

                
                "case_like":self_posted_cases+Complaint.objects.filter(bookmark=user).count()+Complaint.objects.filter(likes=user).count(),

                
                "news_post_like":self_posted_NewArticals+NewsArticalPost.objects.filter(bookmark=user).count()+NewsArticalPost.objects.filter(likes=user).count(),

            
                "artical_like":self_posted_artical+Articals.objects.filter(bookmark=user).count()+Articals.objects.filter(likes=user).count(),
            
                
                "college_story_likes":self_posted_college_story+College_Story.objects.filter(bookmark=user).count()+College_Story.objects.filter(likes=user).count(),

                
                "poll_likes":self_posted_poll+Poll.objects.filter(bookmark=user).count()+Poll.objects.filter(likes=user).count(),
                
                

                }
        elif requestedprofile is not None  and username_id is not None:
            status_data={
                "follow":profile.follow.count(),
                "followStatus":profile.follow.filter(id=username_id).exists(),
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
            return Response({"message":"profile  not exists","status":False,"exception":str(e)},status=400)
        
      

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
            return Response({"message":"profile  not exists","status":False,"exception":str(e)},status=400)
        
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
                                  
        response={
            "ug_course":list_of_ug_degree,
            "pg_course":list_of_pg_degree,
            "department":deparments,
            "ug_institute":ug_of_institute,
            "pg_institute":pg_of_institute,
            "hightest_qualification":[ qual.qualification for qual in HigherQualification.objects.all() ]  
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
            return Response({"message":"resume id not found","status":False},status=404)
        data['upload_file']=request.FILES['upload_file'] 
        
        serializer=ResumeUploadSerializers(get_resume_id, data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Document uploaded successfully","status":True},status=200)
        return Response(serializer.errors,status=400)
    
    def delete(self,request):
        resume_id=request.GET.get('resume_id')
        get_object_or_404(ResumeUpload,id=resume_id).delete()
        return Response({"message":"file deleted","status":True},status=200) 


"""BASED ON SPECIALITY CURRENT JOB LOCATION AND QUELIFICATION MATCH PEOPLE SIMILAR"""
class MatchPeople(APIView):
    def get(self,request):
        userid=request.GET.get('user_id')
        requesteduserid=request.GET.get('requested_user_id')
        response={}
        userdata=Identification.objects.get(userdetail__id=userid)
        
        query=Q( ~Q(userdetail__id=userdata.userdetail.id)
                
                    &
                    Q(
                        Q(current_job_location=userdata.current_job_location)
                        |
                        Q(speciality=userdata.speciality)
                        |
                        Q(hightest_qualification=userdata.hightest_qualification)
                    )
            
            
                )
        matcheddata=Identification.objects.select_related('userdetail').filter(query).order_by("-id")
        
        for match in matcheddata:
            
            followstatus=match.profile_set.filter(follow=userdata.userdetail)

            if followstatus.exists()==False and int(requesteduserid) != match.userdetail.id: 
                serializer=IdentificationSerializers(match,many=False).data 
                try:
                    profileimage=Profile.objects.get(contact=match)
                    serializer["ProfileImage"]=profileimage.image.url
                except Exception as e:
                    serializer["ProfileImage"]="no_image"

               
                serializer["follow"]=False
                
                response[match.id]=serializer  
            else:
                pass
            
        return Response(response.values(),status=status.HTTP_200_OK)

####################################IOS#################################
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
#################################IOS END###############################


############################################################################

"""HOW MANY CASE POSTED BY PARTICULAR USER"""
"""api/user/case?user=171"""
class User_Posted_Case(APIView):
    def get(Self,request):
        #query=request.query_params
        userID=request.GET.get('user_id')
        usernameid=request.GET.get('userid')
        
        response={}
        if userID is not None:
            user=get_object_or_404(User,id=userID)
            query=Q(complaint_id=user)
            

        elif usernameid is not None  :
            user=get_object_or_404(User,id=usernameid)
            query=Q(created_date__lte=date.today())
        else:
            return Response({"message":"key errors","status":False},status=404)
        cases=Complaint.objects.filter(query).order_by("-created_date")
        for case in cases:
            status_data={
                "bookmark_count":case.bookmark.count(),
                "bookmark_status":case.bookmark.filter(id=user.id).exists() if userID is not None or usernameid is not None else False,
                "like_count":case.likes.count(),
                "like_status":case.likes.filter(id=user.id).exists() if userID is not None or usernameid is not None else False,

                        }

            serializer=ComplaintSerializers(case,many=False).data
            profile=Profile.objects.get(contact__userdetail__id=case.complaint_id.id)
            serializer["ProfileName"]=profile.contact.profile_name
            serializer["current_job_location"]=profile.contact.current_job_location
            serializer["speciality"]=profile.contact.speciality
            serializer["hightest_qualification"]=profile.contact.hightest_qualification
            serializer["ProfileImage"]=profile.profileImage.url if profile.profileImage else "no image"
            serializer["discussions"]=case.discussions_set.all().count()
            serializer["follow"]="uploader"
            serializer["poll_status"]=False
            serializer["art_status"]=False
            serializer['PG_NEET']=False
            serializer['newsartical']=False
            serializer['SS_NEET']=False
            serializer["complaint_status"]=True 
            serializer["userid"]=case.complaint_id.id               
            
            serializer.update(status_data)
            response[case.id]=serializer
        return Response(response.values(),status=status.HTTP_200_OK)
        

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
                               
                                "ProfileName":profile.contact.profile_name,
                                "current_job_location":profile.contact.current_job_location,
                                "speciality":profile.contact.speciality,
                                "hightest_qualification":profile.contact.hightest_qualification,
                                "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
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
                                        "ProfileName":profile.contact.profile_name,
                                        "current_job_location":profile.contact.current_job_location,
                                        "speciality":profile.contact.speciality,
                                        "hightest_qualification":profile.contact.hightest_qualification,
                                        "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
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
                                    "ProfileName":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
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
                                    "ProfileName":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
                                    
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
                                    "ProfileName":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
                                })
                serializer.update(status_data)
                response[newspost.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)


"""HOW MANY ARTICAL POSTED BY PARTICULAR USER"""
class User_Posted_Artical(APIView):
    def get(Self,request):
        userid=request.GET.get('user_id')
        usernameid=request.GET.get('userid')
        
        response={}
        if userid is not None:
            user=get_object_or_404(User,id=userid)
            query=Q(user=user)
        elif usernameid is not  None:
            user=get_object_or_404(User,id=usernameid)
            query=Q(created_date__lte=date.today())
        else:
            return Response({"message":"key error","status":False},status=404)
        articals=Articals.objects.filter(query).order_by('-created_date')
        for artical in articals:
            status_data={
                "bookmark_count":artical.bookmark.count(),
                "bookmark_status":artical.bookmark.filter(id=user.id).exists() if userid is not None or usernameid is not  None  else False,
                "like_count":artical.likes.count(),
                "like_status":artical.likes.filter(id=user.id).exists() if userid is not None or usernameid is not  None else False,

                        }

            serializer=ArticalsSerializers(artical,many=False).data
            profile=Profile.objects.get(contact__userdetail__id=artical.user.id)
            serializer['ProfileName']=profile.contact.profile_name
            serializer['current_job_location']=profile.contact.current_job_location
            serializer['speciality']=profile.contact.speciality
            serializer['hightest_qualification']=profile.contact.hightest_qualification
            serializer['ProfileImage']=profile.profileImage.url if profile.profileImage else "no image"
            serializer['follow']="uploader"
            serializer['poll_status']=False
            serializer['art_status']=True 
            serializer['PG_NEET']=False
            serializer['newsartical']=False
            serializer['SS_NEET']=False
            serializer['complaint_status']=False
            serializer['userid']=artical.user.id
            serializer.update(status_data)
            response[artical.id]=serializer
        return Response(response.values(),status=status.HTTP_200_OK)
       


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
                        "ProfileName":profile.contact.profile_name,
                        "current_job_location":profile.contact.current_job_location,
                        "speciality":profile.contact.speciality,
                        "hightest_qualification":profile.contact.hightest_qualification,
                        "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
                        
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
                
                serializer=ArticalsSerializers(artical,many=False).data
                profile=Profile.objects.get(contact__userdetail__id=artical.user.id)
                serializer['ProfileName']=profile.contact.profile_name
                serializer['current_job_location']=profile.contact.current_job_location
                serializer['speciality']=profile.contact.speciality
                serializer['hightest_qualification']=profile.contact.hightest_qualification
                serializer['ProfileImage']=profile.profileImage.url if profile.profileImage else "no image"
                serializer['bookmark_count']=artical.bookmark.all().count()
                serializer['bookmark_status']=artical.bookmark.filter(id=user.id).exists()
                serializer['like_count']=artical.likes.count()
                serializer['like_status']=artical.likes.filter(id=user.id).exists()
                
                
                
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
                                    "ProfileName":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
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
                                    "ProfileName":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
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
                                    "ProfileName":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
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
        userid=request.GET.get('user_id')
        usernameid=request.GET.get('userid')
        
        response={}
        if userid is not None:
            user=get_object_or_404(User,id=userid)
            query=Q(poll_user=user)
        elif usernameid is not None:
            user=get_object_or_404(User,id=usernameid)
            query=Q(created_date__lte=date.today())
        else :
            query=Q(created_date__lte=date.today())
            #return Response({"message":"key error","status":False})
        
        polls=Poll.objects.filter(query).order_by('-created_date')
        
        for poll in polls:
            
            try:
                user_poll_status=PollVote.objects.get(poll_id=poll,profile=user)
                
                userstatus={
                        "user_status":True,
                        "choice": user_poll_status.choice 
                        }
            except Exception as e:
                userstatus={
                        "user_status":False,
                        "choice": "no_opinion"
                        }
           
            tvote=poll.pollvote_set.all().count()
            vote=PollVote.objects.aggregate(
                        # TOTAL=Count()
                        A=Count('pk', filter=Q(poll_id=poll,choice="A")),
                        B=Count('pk', filter=Q(poll_id=poll,choice="B")),
                        C=Count('pk', filter=Q(poll_id=poll,choice="C")),
                        D=Count('pk', filter=Q(poll_id=poll,choice="D"))

                                        )
            
            status_data={
                "bookmark_count":poll.bookmark.count(),
                "bookmark_status":poll.bookmark.filter(id=user.id).exists() if userid is not None or usernameid is not None  else False ,
                "like_count":poll.likes.count(),
                "like_status":poll.likes.filter(id=user.id).exists() if userid is not None or usernameid is not None else False,
               
                "vote":tvote,
                "A": vote["A"] if vote["A"]==0 else int((vote["A"]/tvote)*100 ),
                "B": vote["B"] if vote["B"]==0 else int((vote["B"]/tvote)*100),
                "C": vote["C"] if vote["C"]==0 else int((vote["C"]/tvote)*100),
                "D": vote["D"] if vote["D"]==0 else int((vote["D"]/tvote)*100),
                
                "discussion":poll.pollcomment_set.count()

                        }
           
            status_data.update(userstatus)

            serializer=PollSerializers(poll,many=False).data
            profile=Profile.objects.get(contact__userdetail__id=poll.poll_user.id)
            serializer['ProfileName']=profile.contact.profile_name
            serializer['current_job_location']=profile.contact.current_job_location
            serializer['speciality']=profile.contact.speciality
            serializer['hightest_qualification']=profile.contact.hightest_qualification
            serializer['ProfileImage']=profile.profileImage.url if profile.profileImage else "no image"
            serializer['follow']="uploader"
            serializer['poll_status']=True
            serializer['art_status']=False
            serializer['PG_NEET']=False
            serializer['newsartical']=False
            serializer['SS_NEET']=False
            serializer['complaint_status']=False
            serializer["userid"]=poll.poll_user.id
            serializer.update(status_data)
            response[poll.id]=serializer
        return Response(response.values(),status=status.HTTP_200_OK)
        





"""HOW MANY  POLL BOOKMARK BY PARTICULAR USER"""
class User_Poll_Bookmarks(APIView):
    def get(self,request):
        query=request.query_params
        
        response={}
        if query['user_id']:
            user=get_object_or_404(User,id=query['user_id'])
            polls=Poll.objects.filter(bookmark=user)
            for poll in polls:
                user_poll_status=poll.pollvote_set.filter(profile=user)

                vote=poll.pollvote_set.aggregate(
                            TOTAL=Count('poll_id'), 
                            A=Count('pk', filter=Q(choice="A")),
                            B=Count('pk', filter=Q(choice="B")),
                            C=Count('pk', filter=Q(choice="C")),
                            D=Count('pk', filter=Q(choice="D")),
                        )
                status_data={
                    "bookmark_count":poll.bookmark.all().count(),
                    "bookmark_status":poll.bookmark.filter(id=user.id).exists(),
                    "like_count":poll.likes.count(),
                    "like_status":poll.likes.filter(id=user.id).exists(),
                    "user_status":user_poll_status.exists(),
                    "vote":vote["TOTAL"],
                    "A": vote["A"] if vote["A"]==0 else int((vote["A"]/vote["TOTAL"])*100),
                    "B": vote["B"] if vote["B"]==0 else int((vote["B"]/vote["TOTAL"])*100),
                    "C": vote["C"] if vote["C"]==0 else int((vote["C"]/vote["TOTAL"])*100),
                    "D": vote["D"] if vote["D"]==0 else int((vote["D"]/vote["TOTAL"])*100),
                    "choice": user_poll_status[0].choice if user_poll_status.exists() else "no_opinion"

                            }

                serializer=PollSerializers(poll,many=False).data
                profile=Profile.objects.get(contact__userdetail__id=poll.poll_user.id)
                
                serializer.update(
                                {
                                   
                                    "ProfileName":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
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
                vote=poll.pollvote_set.aggregate(
                            TOTAL=Count('poll_id'), 
                            A=Count('pk', filter=Q(choice="A")),
                            B=Count('pk', filter=Q(choice="B")),
                            C=Count('pk', filter=Q(choice="C")),
                            D=Count('pk', filter=Q(choice="D")),
                        )

                status_data={
                    "bookmark_count":poll.bookmark.all().count(),
                    "bookmark_status":poll.bookmark.filter(id=user.id).exists(),
                    "like_count":poll.likes.count(),
                    "like_status":poll.likes.filter(id=user.id).exists(),
                    "user_status":user_poll_status.exists(),
                    "vote":vote["TOTAL"],
                    "A": vote["A"] if vote["A"]==0 else int((vote["A"]/vote["TOTAL"])*100),
                    "B": vote["B"] if vote["B"]==0 else int((vote["B"]/vote["TOTAL"])*100),
                    "C": vote["C"] if vote["C"]==0 else int((vote["C"]/vote["TOTAL"])*100),
                    "D": vote["D"] if vote["D"]==0 else int((vote["D"]/vote["TOTAL"])*100),
                    "choice": user_poll_status[0].choice if user_poll_status.exists() else "no_opinion"
                    

                            }

                serializer=PollSerializers(poll,many=False).data
                profile=Profile.objects.get(contact__userdetail__id=poll.poll_user.id)
                
                serializer.update(
                                {
                                    "ProfileName":profile.contact.profile_name,
                                    "current_job_location":profile.contact.current_job_location,
                                    "speciality":profile.contact.speciality,
                                    "hightest_qualification":profile.contact.hightest_qualification,
                                    "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
                                    "follow":"uploader"
                                    
                                })  
                serializer.update(status_data)
                response[poll.id]=serializer
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error"},status=status.status.HTTP_400_BAD_REQUEST)

##########################################################################






'''api/job/category/'''
'''category of job just like covid duety'''
class Category(APIView):
    def get(self,request,format=None): 
        job_category=Job_By_Category.objects.all()
        return Response(Job_By_CategorySerializers(job_category,many=True).data,status=200)
    
"""Hospital data"""  
def hospitalinfo(name,location):
    # try:
    hospital=HospitalInfo.objects.get(name__iexact=name,location__iexact=location)
    banner=hospital.hospitalbanner_set.all()
    highlight=hospital.hospitalhighlight_set.all()
    speciality=hospital.hospitalspeciality_set.all()
    serializers=HospitalInfoSerializers(hospital,many=False).data
    serializers['banner']=[{"id":i.id,"image":i.file.url} for i in banner]
    serializers['highlight']=[{"id":i.id,"title":i.title,"image":i.file.url} for i in highlight]
    serializers['speciality']=[{"id":i.id,"title":i.title,"image":i.file.url} for i in speciality]
    # except Exception as e:
    #     return Response({"message":str(e)})
    return serializers

    
'''api/new/job/'''
'''new job post'''
class JobPost(APIView):
    
    def get(self,request):
        
        new_job_id=request.GET.get('jobid')
        username_id=request.GET.get('user_id')
        categoryId=request.GET.get('categoryid')
        pagerequest=request.GET.get('page')
        resp={}


        try:
            user=User.objects.get(id=username_id)
        except Exception as e:
            return Response({"message":"user not found","status":False},status=400)
        
        
        
        if new_job_id is not None and username_id is not None:
           
            
            try:
                jobid=Category_Related_Job.objects.get(id=new_job_id)
                
            except Exception as e:
                return Response({"message":"job not exists","exception":str(e)},status=404) 
            
            serializer=Category_Related_JobSerializers(jobid,many=False).data
            serializer['eligibility']=[ {"name":i} for i in jobid.qualification.split(",")]
            serializer["bookmark"]=jobid.bookmark.filter(id=user.id).exists()
            serializer["likes"]=jobid.likes.filter(id=user.id).exists()
            serializer["apply_status"]=jobid.applicant.filter(id=user.id).exists()
            serializer["hopitla"]=hospitalinfo(jobid.hosptial_name,jobid.location)

            return Response(serializer,status=200)  
        
        elif categoryId is not None and username_id is not None:
               
            
            try:
                category=Job_By_Category.objects.get(id=categoryId)
                
            except Exception as e:
                return Response({"message":"category id not exists","exception":str(e)},status=404) 
            
            jobs=Category_Related_Job.objects.select_related('category').filter(category=category,job_status=True).order_by("-created_date")
            for jobid in jobs:
                serializer=CategoryRelatedJobSerializers(jobid,many=False).data
                serializer['eligibility']=[ {"name":i} for i in jobid.qualification.split(",")]
                serializer["bookmark"]=jobid.bookmark.filter(id=user.id).exists()
                resp[jobid.id]=serializer  
            pageitem = Paginator(list(resp.values()), 5) 
            requestpage=pageitem.page(int(pagerequest)) 
            return Response(requestpage.object_list,status=200)  
             
        elif  username_id is not None:
            
            department=Identification.objects.get(userdetail=user)
            job_id=Category_Related_Job.objects.filter(job_status=True,Speciality=department.speciality).order_by('-created_date')
          
            for category in job_id:
                
                serializers=CategoryRelatedJobSerializers(category,many=False).data
                serializers['bookmark']=category.bookmark.filter(id=username_id).exists()
                serializers['eligibility']=[ {"name":i} for i in category.qualification.split(",")]
                resp[category.id]=serializers
            
            jobs=Category_Related_Job.objects.filter( Q(job_status=True) & ~Q(Speciality=department.speciality) ).order_by('-created_date')
            
            for job in jobs:
                serializers=CategoryRelatedJobSerializers(job,many=False).data
                serializers['eligibility']=[ {"name":i} for i in job.qualification.split(",")]
                serializers['bookmark']=job.bookmark.filter(id=username_id).exists()
                resp[job.id]=serializers

            pageitem = Paginator(list(resp.values()), 5) 
            requestpage=pageitem.page(int(pagerequest)) 
            
            return Response(requestpage.object_list,status=200)
        else:
            return Response({"message":"Key errors something passing wrong","status":False},status=400)
            
"""RANDOM JOB SHOW EXCLUDE SELETED JOB ID"""   
'''api/new/job/random?job_id=5&user_id=185'''
'''new job post'''
class RandomJobs(APIView):
    
    def get(self,request):
        
        jobid=request.GET.get('job_id')
        userid=request.GET.get('user_id')
        resp={}
        try:
            user=User.objects.get(id=userid)
        except Exception as e:
            return Response({"message":"user not found","status":False},status=400)
        
        try:
            Category_Related_Job.objects.get(id=jobid)
        except Exception as e:
            return Response({"message":"job id not found","status":False},status=400)
        
    
        if  userid is not None and jobid is not None :
              
            job_id=list(Category_Related_Job.objects.filter(job_status=True).exclude(id=jobid) )
            random.shuffle(job_id)
            for category in job_id:
                serializers=Category_Related_JobSerializers(category,many=False).data
                serializers['eligibility']=[ {"name":i} for i in category.qualification.split(",")]
                serializers['apply_status']=category.applicant.filter(id=userid).exists()
                serializers['likes']=category.likes.filter(id=userid).exists()
                serializers['bookmark']=category.bookmark.filter(id=userid).exists()
                resp[category.id]=serializers
             
            return Response(resp.values(),status=200)
        else:
            return Response({"message":"Key errors something passing wrong","status":False},status=400)   



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
        for i in range(len(deparments)):  
            response[i]={
                "id":i+1,
                "department":deparments[i],
                
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


"""HOSPITAL TYPE LIST"""
class Hospital_Type_Lists(APIView):
    def get(self,request):
        HT= Hospital_Type.objects.all()
        serializers=HospitalTypeSerializer(HT,many=True)
        return Response(serializers.data)

class CategoriesData(APIView):
    def get(self,request,):
        category=request.GET.get('category')
        for i in categories:
            if i.get(category):
                return Response(i[category])
        return Response({"message":"category name not found","name":category})
                

class CategoryDesignation(APIView):
    def get(self,request,category):
        for i in categoryDesignation:
            if i.get(category):
                return Response(i[category])
        return Response({"message":"Category has no any designation wait for update","name":category,"status":False})


#############################LIKE BOOKMARK FOLLOW AND UNFOLLOW######################################

""""LIKE BOOKMARK AND APPLY JOB"""
class Likes(APIView):
    def get(self,request,format=None):
        username_id=request.GET.get('user_id')
        category_job_id=request.GET.get('job_id')
        try:
            user=User.objects.get(id=username_id)
            
        except Exception as e:
            return Response({"message":str(e),"status":False},status=status.HTTP_400_BAD_REQUEST)
        try:
            Category_Related_Job.objects.get(id=category_job_id,likes=user) 
            return Response({"likes":True,"status":True},status=status.HTTP_200_OK)  
        except Exception as e:
             return Response({"likes":False,"status":False},status=status.HTTP_400_BAD_REQUEST)
        
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
            return Response({"message":str(e),"status":False},status=status.HTTP_400_BAD_REQUEST)

        if username_id and category_job_id:
            
               
            try:
                job_likes=Category_Related_Job.objects.get(id=category_job_id)
            except Exception as e:
                return Response({"message":"jobs id not found","status":False,"exception":str(e)},status=400)
            try:
                if job_likes.likes.get(id=user.id):
                    job_likes.likes.remove(user)
                    return Response({"likes":False,"status":False,"like_count":job_likes.likes.all().count()},status=200)
            except Exception as e:
                job_likes.likes.add(user)
                return Response({"likes":True,"status":True,"like_count":job_likes.likes.all().count()},status=200)
            return Response({"message":"error find check and try again","status":True},status=400)
        
        elif username_id and complaintId:
            
           
            try:
                complaint=Complaint.objects.get(id=complaintId)
            except Exception as e:
                return Response({"message":"complaint id not found","status":False,"exception":str(e)},status=400)
            try:
                if complaint.likes.get(id=user.id):
                    complaint.likes.remove(user)
                    return Response({"likes":False,"status":False,"like_count":complaint.likes.all().count()},status=200)
            except Exception as e:
                complaint.likes.add(user)
                return Response({"likes":True,"status":True,"like_count":complaint.likes.all().count()},status=200)
            return Response({"message":"error find check and try again","status":True},status=400)

        elif username_id and pollId:
            
            try:
                poll=Poll.objects.get(id=pollId)
            except Exception as e:
                return Response({"message":"poll id not found","status":False,"exception":str(e)},status=400)
            try:
                if poll.likes.get(id=user.id):
                    poll.likes.remove(user)
                    return Response({"likes":False,"status":False,"like_count":poll.likes.all().count()},status=200)
            except Exception as e:
                poll.likes.add(user)
                return Response({"likes":True,"status":True,"like_count":poll.likes.all().count()},status=200)
            return Response({"message":"error find check and try again","status":True},status=400)

        elif username_id and new_articalId:
            
            try:
                artical=NewsArticalPost.objects.get(id=new_articalId)
            except Exception as e:
                return Response({"message":"News Artical id not found","status":False,"exception":str(e)},status=400)
            try:
                if artical.likes.get(id=user.id):
                    artical.likes.remove(user)
                    return Response({"likes":False,"status":False,"like_count":artical.likes.all().count()},status=200)
            except Exception as e:
                artical.likes.add(user)
                return Response({"likes":True,"status":True,"like_count":artical.likes.all().count()},status=200)
            return Response({"message":"error find check and try again","status":True},status=400)

        elif username_id and articalID:
            
            try:
                artical=Articals.objects.get(id=articalID)
            except Exception as e:
                return Response({"message":"Artical id not found","status":False,"exception":str(e)},status=400)
            try:
                if artical.likes.get(id=user.id):
                    artical.likes.remove(user)
                    return Response({"likes":False,"status":False,"like_count":artical.likes.all().count()},status=200)
            except Exception as e:
                artical.likes.add(user)
                return Response({"likes":True,"status":True,"like_count":artical.likes.all().count()},status=200)
            return Response({"message":"error find check and try again","status":True},status=400)

        else:
            return Response({"errors":"key error","status":False},status=200)

'''Add bookmark'''
'''api/job/bookmark/'''    
class BookMark(APIView):
    def get(self,request,format=None):
        username_id=request.GET.get('user_id')
        
        resp={}
        try:
            user=User.objects.get(id=username_id)
        except Exception as e:
            return Response({"message":str(e),"status":False})
       
        job_categorys=Category_Related_Job.objects.filter(bookmark=user)
        
        if not job_categorys.exists():
            return Response(resp.values(),status=200)

        else:
            for category in job_categorys:
                
                serializer=Category_Related_JobSerializers(category,many=False).data
                serializer['eligibility']=[ {"name":i} for i in category.qualification.split(",")]
                serializer["bookmark"]=category.bookmark.filter(id=user.id).exists()
                serializer["likes"]=category.likes.filter(id=user.id).exists()
                serializer["apply_status"]=category.applicant.filter(id=user.id).exists()
                resp[category.id]=serializer
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
            return Response({"message":str(e),"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        if username_id and category_job_id:
            try:
                job_likes=Category_Related_Job.objects.get(id=category_job_id)
            except Exception as e:
                return Response({"message":"jobs id not found","status":False,"exception":str(e)},status=400)
            try:
                if job_likes.bookmark.get(id=user.id):
                    job_likes.bookmark.remove(user)
                    return Response({"bookmark":False,"status":False},status=200)
            except Exception as e:
                job_likes.bookmark.add(user)
                return Response({"bookmark":True,"status":True},status=200)
        
        elif username_id and news_arctical:
            try:
                artical=NewsArticalPost.objects.get(id=news_arctical)
            except Exception as e:
                return Response({"message":"News Artical id not found","status":False,"exception":str(e)},status=400)
            try:
                if artical.bookmark.get(id=user.id):
                    artical.bookmark.remove(user)
                    return Response({"bookmark":False,"status":False},status=200)
            except Exception as e:
                artical.bookmark.add(user)
                return Response({"bookmark":True,"status":True},status=200)

        elif username_id and articalID:
            try:
                artical=Articals.objects.get(id=articalID)
            except Exception as e:
                return Response({"message":"Artical id not found","status":False,"exception":str(e)},status=400)
            try:
                if artical.bookmark.get(id=user.id):
                    artical.bookmark.remove(user)
                    return Response({"bookmark":False,'status':False},status=200)
            except Exception as e:
                artical.bookmark.add(user)
                return Response({"bookmark":True,"status":True},status=200)

        elif username_id and poll:
            try:
                single_poll=Poll.objects.get(id=poll)
            except Exception as e:
                return Response({"message":"poll id not found","status":False,"exception":str(e)},status=400)
            try:
                if single_poll.bookmark.get(id=user.id):
                    single_poll.bookmark.remove(user)
                    return Response({"bookmark":False,"status":False},status=200)
            except Exception as e:
                single_poll.bookmark.add(user)
                return Response({"bookmark":True,"status":True},status=200)

        
        elif username_id and complaint:
            try:
                case=Complaint.objects.get(id=complaint)
            except Exception as e:
                return Response({"message":"complaint id not found","status":False,"exception":str(e)},status=400)
            try:
                if case.bookmark.get(id=user.id):
                    case.bookmark.remove(user)
                    return Response({"bookmark":False,"status":False},status=200)
            except Exception as e:
                case.bookmark.add(user)
                return Response({"bookmark":True,"status":True},status=200)
        
        



        return Response({"message":"error find check and try again","status":True},status=400)

"""GET FOLLOWING PROFILE"""
class FollowingProfile(APIView):
    def get(self,request):
        username_id=request.GET.get('user_id')
        response={}
        try:
            followingprofile=Profile.objects.filter(follow=get_object_or_404(User,id=username_id))
        except Exception as e:
            return Response({"message":str(e),"status":False},status=status.HTTP_400_BAD_REQUEST)
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
            return Response({"message":str(e),"status":False},status=status.HTTP_400_BAD_REQUEST)
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
                return Response({"message":str(e),"status":False},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                author=Profile.objects.select_related('contact').get(contact__userdetail__id=followid)
            except Exception as e:
                return Response({"message":"follow id not found","status":False,"exception":str(e)},status=400)
            try:
                if author.follow.get(id=user.id):
                    author.follow.remove(user)
                    return Response({"follow":False,"status":False},status=200)
            except Exception as e:
                author.follow.add(user)
                return Response({"follow":True,"status":True},status=200)
        else:
            return Response({"message":"you can not follow own profile","status":False},status=400)


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
            return Response({"message":str(e),"status":False},status=status.HTTP_400_BAD_REQUEST)
       
        job_categorys=Category_Related_Job.objects.filter(applicant=user)
        
        for category in job_categorys:
            
            serializer=Category_Related_JobSerializers(category,many=False).data
            serializer["bookmark_status"]=category.bookmark.filter(id=user.id).exists()
            serializer["like_status"]=category.likes.filter(id=user.id).exists()
            serializer["apply_status"]=category.applicant.filter(id=user.id).exists()

            resp[category.id]=serializer
            
        return Response(resp.values(),status=200)
    
    def post(self,request,format="json"):
        username_id=request.GET.get('user_id')
        category_job_id=request.GET.get('job_id')
        try:
            user=User.objects.get(id=username_id)
        except Exception as e:
            return Response({"message":str(e),"status":False},status=status.HTTP_400_BAD_REQUEST)
           
        try:
            job_application=Category_Related_Job.objects.get(id=category_job_id)
        except Exception as e:
            return Response({"message":"jobs id not found","status":False,"exception":str(e)},status=400)
        try:
            if job_application.applicant.get(id=user.id):
                job_application.applicant.remove(user)
                return Response({"apply_status":False,"status":False},status=200)
        except Exception as e:
            job_application.applicant.add(user)
            return Response({"apply_status":True,"status":True},status=200)
        return Response({"message":"error find check and try again","status":True},status=400)
        


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
                return Response({"message":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
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
                return Response({"message":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
            
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
        return Response({"message":"poll comment posted","status":True,"poll_comment":poll_comment},status=200)
    
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
            
        else:
            query_set=Q(created_date__date__lte=date.today())
           
        newsartical=NewsArticalPost.objects.select_related('userid').filter(query_set).order_by('-created_date')
        print(newsartical)
        for artical in newsartical:
            serializer=NewsArticalPostSerializers(artical,many=False).data
           
            
            
            response[artical.id]=serializer
            try:
                profile=Profile.objects.select_related('contact').get(contact__userdetail__id=artical.userid.id)
            except Exception as e:
                pass
            else:
                response[artical.id].update({
                    "username":profile.contact.profile_name,
                    "profileImage":profile.profileImage.url if profile.profileImage else "no image",
                    "speciality":profile.contact.speciality if profile.contact.speciality is not None else "notfilled",
                    "current_job_location":profile.contact.current_job_location
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
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"news artical posted","status":True},status=200)
        return Response({"message":"errors","status":False},status=400)

###############################
""" TESTING OF PAGINATION"""

class NewsArticalPostT(APIView):
    def get(self,request):
       
        pagerequest=request.GET.get('page')

        response={}
        
           
        newsartical=NewsArticalPost.objects.select_related('userid').all().order_by('-created_date')
       
        serializers=NewsArticalPostSerializers(newsartical,many=True)
        pageitem=Paginator(serializers.data,5)
        requestpage=pageitem.page(int(pagerequest))
        # response={
        #     "items":pagecount,
        #     "totalpage":numberofpages,
        #     "nextpages":requestpage.has_next(),
        #     "previouspages":requestpage.has_previous(),
        #     "nextpage":requestpage.next_page_number(),
        #     "priviouspage":requestpage.previous_page_number() if requestpage.has_previous() else None,
        #     "startpage":requestpage.start_index(),
        #     "endpage":requestpage.end_index(),
        #     "post":requestpage.object_list
        # }
        #serializers.data[0].update(response)
        return Response(requestpage.object_list,status=200)



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
                "create_date":artical.created_date,
                "speciality":comment_profile.contact.speciality if comment_profile.contact.speciality is not None else "notfilled"

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
        return Response({"message":"artical comment posted","status":True,"artical_comment":artical_comment},status=200)

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
        return Response({"message":"artical comment posted","status":True,"discussion":total_discussion},status=200)

"""COMPLAINT POST AND COMMENT API END"""




""""THIS IS FOR HOME PAGE API IT HAS COMPLAINT,POLL,ARTICAL THIS IS BASE ON CREATED DATE"""
"""news/poll/complaint/"""

class ComplaintAndPolls(APIView):
    def get(self,request):
        
        response={}
        pagerequest=request.GET.get('page')
        username_id=request.GET.get('user_id')
        polls=Poll.objects.values('created_date')
        complaints=Complaint.objects.values('created_date')
        NewArtical=Articals.objects.values('created_date')
        question=Question.objects.values('created_date')
        newsartical=NewsArticalPost.objects.values('created_date')
       
        fivejoin=polls.union(complaints,NewArtical,question,newsartical).order_by('-created_date')
        pageitem = Paginator(list(fivejoin), 5) 
        requestpage=pageitem.page(int(pagerequest)) 
       
        
        
        user=get_object_or_404(User,id=username_id)
        
        
        
        for i in range(len(requestpage.object_list)):
            try:
                poll=Poll.objects.prefetch_related("likes","bookmark").get(created_date=requestpage.object_list[i]['created_date'])
                
                
           
            
                
                serializer=PollVoteSerializers(poll,many=False).data
                poll_pro=Profile.objects.select_related('contact').get(contact__userdetail__id=poll.poll_user.id)
                
                poll_profile={  
                                "userid":poll.poll_user.id,
                                "ProfileName":poll_pro.contact.profile_name,
                                "ProfileImage":poll_pro.profileImage.url if poll_pro.profileImage else "no image",
                                "speciality":poll_pro.contact.speciality,
                                "location":poll_pro.contact.current_job_location
                            }
                serializer.update(poll_profile)
                
                find_existing_voter_or_not=PollVote.objects.select_related('poll','profile').filter(poll_id__id=poll.id,profile__id=user.id)
                

                tvote=poll.pollvote_set.count()

                vote=PollVote.objects.aggregate(
                        # TOTAL=Count(filter=Q(poll_id=poll)),
                        A=Count('pk', filter=Q(poll_id=poll,choice="A")),
                        B=Count('pk', filter=Q(poll_id=poll,choice="B")),
                        C=Count('pk', filter=Q(poll_id=poll,choice="C")),
                        D=Count('pk', filter=Q(poll_id=poll,choice="D"))

                                        )
    
                

                if user.id != poll_pro.contact.userdetail.id:
                    follow=poll_pro.follow.filter(id=user.id).exists()
                else:
                    follow="uploader"
                

                like=poll.likes.filter(id=user.id)

                poll_comment=PollComment.objects.filter(poll_id__id=poll.id)


                bookmark=poll.bookmark.filter(id=user.id)
                serializer["SS_NEET"]= False
                serializer["PG_NEET"]= False 
                serializer["newsartical"]= False 
               
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
                                "vote":tvote,
                                "A": vote["A"] if vote["A"]==0 else int((vote["A"]/tvote)*100 ),
                                "B": vote["B"] if vote["B"]==0 else int((vote["B"]/tvote)*100),
                                "C": vote["C"] if vote["C"]==0 else int((vote["C"]/tvote)*100),
                                "D": vote["D"] if vote["D"]==0 else int((vote["D"]/tvote)*100),
                                "choice":find_existing_voter_or_not[0].choice if find_existing_voter_or_not.exists() else "no_opinion" ,
                                "discussion":poll_comment.count()
                   
                                })
                
                response[datetime.now()]=serializer
            except Exception as e:
                pass
            try:
                complaint=Complaint.objects.get(created_date=requestpage.object_list[i]['created_date'])
           
            
                serializer1=CaseSerializers(complaint,many=False).data
                complaint_profile=Profile.objects.select_related('contact').get(contact__userdetail__id=complaint.complaint.id)
                case_profile={
                            "userid":complaint.complaint.id,
                            "ProfileName":complaint_profile.contact.profile_name,
                            "ProfileImage":complaint_profile.profileImage.url if complaint_profile.profileImage else "no image",
                            "speciality":complaint_profile.contact.speciality,
                            "location":complaint_profile.contact.current_job_location
                            }
                
                serializer1.update(case_profile)

                discussion=Discussions.objects.select_related('case','profile').filter(case_id__id=complaint.id)
                if user.id != complaint_profile.contact.userdetail.id:
                    follow=complaint_profile.follow.filter(id=user.id).exists()
                else:
                    follow="uploader"
               
                like=complaint.likes.filter(id=user.id)
                bookmark=complaint.bookmark.filter(id=user.id)
                serializer1['bookmark_status']=bookmark.exists()
                serializer1['bookmark_count']=complaint.bookmark.count()
                serializer1['like_status']=like.exists()
                serializer1['like_count']=complaint.likes.count()
                serializer1['discussion']=discussion.count()
                serializer1['follow']=str(follow)
                serializer1['poll_status']=bookmark.exists()
                serializer1['art_status']=bookmark.exists()
                serializer1["SS_NEET"]= False
                serializer1["PG_NEET"]= False 
                serializer1["newsartical"]= False 
                

                response[datetime.now()]=serializer1
            except Exception as e:
                pass
            try: 
                artical=Articals.objects.get(created_date=requestpage.object_list[i]['created_date'])
            
                serializer2=ArticalSerializers(artical,many=False).data
               
                artical_profile=Profile.objects.get(contact__userdetail__id=artical.user.id)
                case_profile={
                                "userid":artical.user.id,
                                "ProfileName":artical_profile.contact.profile_name,
                                "ProfileImage":artical_profile.profileImage.url if artical_profile.profileImage else "no image",
                                "speciality":artical_profile.contact.speciality,
                                "location":artical_profile.contact.current_job_location
                            }
                serializer2.update(case_profile)

                if user.id != artical_profile.contact.userdetail.id:
                    follow=artical_profile.follow.filter(id=user.id).exists()
                else:
                    follow="uploader"

                artical_comment=artical.articalcomment_set.all().count()
                #follow=artical_profile.follow.filter(id=user.id)
                like=artical.likes.filter(id=user.id)
                bookmark=artical.bookmark.filter(id=user.id)
                serializer2["SS_NEET"]= False
                serializer2["PG_NEET"]= False 
                serializer2["complaint_status"]= False
                serializer2["poll_status"]= False 
                serializer2["discussion"]= artical_comment
                serializer2["follow"]= str(follow)
                serializer2["like_count"]= artical.likes.count()
                serializer2["like_status"]= like.exists()
                serializer2["art_status"]=True
                serializer2["bookmark_status"]= bookmark.exists()
                serializer2["bookmark_count"]= artical.bookmark.all().count()
                serializer2["newsartical"]= False
                
                response[datetime.now()]=serializer2
            except Exception as e:
                pass 
            try:
                question=Question.objects.get(created_date=requestpage.object_list[i]['created_date'])
           
                serializer=QuestionSerializers(question,many=False).data
                serializer["ProfileImage"]=question.ProfileImage.url if question.ProfileImage  else "no image"
                serializer["complaint_status"]=False 
                serializer["poll_status"]=False 
                serializer["art_status"]=False 
                serializer["SS_NEET"]=True if question.exam=="SS-NEET" else False
                serializer["PG_NEET"]=True if question.exam=="PG-NEET" else False 
                serializer["newsartical"]= False
                try:
                    attemptquestion=question.atteptquestion_set.get(user=user,question=question) 
                    serializer['selected_option']=attemptquestion.selected_option
                    serializer['answer_status']=attemptquestion.answer_status
                except Exception as e:
                    serializer['selected_option']=None
                    serializer['answer_status']=False
                response[datetime.now()]=serializer
            except Exception as e:
                pass 
            
            try:
                artical=NewsArticalPost.objects.get(created_date=requestpage.object_list[i]['created_date'])
           
            
                serializer=NewsArticalSerializers(artical,many=False).data
                
                try:
                    profile=Profile.objects.select_related('contact').get(contact__userdetail__id=artical.userid.id)
                except Exception as e:
                    pass
                else:
                    serializer.update({
                        "ProfileName":profile.contact.profile_name,
                        "ProfileImage":profile.profileImage.url if profile.profileImage else "no image",
                        "speciality":profile.contact.speciality if profile.contact.speciality is not None else "notfilled",
                        "location":profile.contact.current_job_location
                    })
                    serializer.update({
                        "bookmark_status":artical.bookmark.filter(id=user.id).exists(),
                        "bookmark_count":artical.bookmark.all().count(),
                        "like_status":artical.likes.filter(id=user.id).exists(),
                        "like_count":artical.likes.all().count(),
                        "follow":profile.follow.filter(id=user.id).exists()
                        
                        })
                    serializer["complaint_status"]=False 
                    serializer["poll_status"]=False 
                    serializer["art_status"]=False 
                    serializer["SS_NEET"]= False
                    serializer["PG_NEET"]= False 
                    serializer["newsartical"]= True
                    response[datetime.now()]=serializer
            except Exception as e:
                pass 
        return Response(response.values())




#############################################testing purpose#################################

class ComplaintAndPoll(APIView):
    def get(self,request):
        response={}
       
        pagerequest=request.GET.get('page')

        username_id=request.GET.get('user_id')

        polls=Poll.objects.values('created_date')
        complaints=Complaint.objects.values('created_date')
        NewArtical=Articals.objects.values('created_date')
        question=Question.objects.values('created_date')
        newsartical=NewsArticalPost.objects.values('created_date')
        
        fivejoin=polls.union(complaints,NewArtical,question,newsartical).order_by('-created_date')
       
        pageitem = Paginator(list(fivejoin),5) 
        requestpage=pageitem.page(int(pagerequest)) 
        
        
        user=get_object_or_404(User,id=username_id)
        
        
        
        for i in range(len(requestpage.object_list)):

            try:
                poll=Poll.objects.select_related("poll_user").filter(created_date=requestpage.object_list[i]['created_date']).prefetch_related("likes","bookmark").get()
                serializer=PollVoteSerializers(poll,many=False).data
                poll_pro=Profile.objects.select_related('contact__userdetail').get(contact__userdetail__id=poll.poll_user.id)
                
                poll_profile={  
                                "userid":poll.poll_user.id,
                                "ProfileName":poll_pro.contact.profile_name,
                                "ProfileImage":poll_pro.profileImage.url if poll_pro.profileImage else "no image",
                                "speciality":poll_pro.contact.speciality,
                                "location":poll_pro.contact.current_job_location
                            }
                serializer.update(poll_profile)
                
                find_existing_voter_or_not=PollVote.objects.select_related('poll','profile').filter(poll_id__id=poll.id,profile__id=user.id)
                

                tvote=poll.pollvote_set.count()

                vote=PollVote.objects.aggregate(
                        # TOTAL=Count(filter=Q(poll_id=poll)),
                        A=Count('pk', filter=Q(poll_id=poll,choice="A")),
                        B=Count('pk', filter=Q(poll_id=poll,choice="B")),
                        C=Count('pk', filter=Q(poll_id=poll,choice="C")),
                        D=Count('pk', filter=Q(poll_id=poll,choice="D"))

                                        )
    
                

                if user.id != poll_pro.contact.userdetail.id:
                    follow=poll_pro.follow.filter(id=user.id).exists()
                else:
                    follow="uploader"
                

                like=poll.likes.filter(id=user.id)

                poll_comment=PollComment.objects.filter(poll_id__id=poll.id)


                bookmark=poll.bookmark.filter(id=user.id)
                serializer["SS_NEET"]= False
                serializer["PG_NEET"]= False 
                serializer["newsartical"]= False 
               
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
                                "vote":tvote,
                                "A": vote["A"] if vote["A"]==0 else int((vote["A"]/tvote)*100 ),
                                "B": vote["B"] if vote["B"]==0 else int((vote["B"]/tvote)*100),
                                "C": vote["C"] if vote["C"]==0 else int((vote["C"]/tvote)*100),
                                "D": vote["D"] if vote["D"]==0 else int((vote["D"]/tvote)*100),
                                "choice":find_existing_voter_or_not[0].choice if find_existing_voter_or_not.exists() else "no_opinion" ,
                                "discussion":poll_comment.count()
                   
                                })
                
                response[datetime.now()]=serializer
            except Exception as e:
                pass
            
                

            try:
                complaint=Complaint.objects.select_related("complaint").filter(created_date=requestpage.object_list[i]['created_date']).prefetch_related("likes","bookmark").get()
                serializer1=CaseSerializers(complaint,many=False).data
                complaint_profile=Profile.objects.select_related('contact__userdetail').get(contact__userdetail__id=complaint.complaint.id)
                case_profile={
                            "userid":complaint.complaint.id,
                            "ProfileName":complaint_profile.contact.profile_name,
                            "ProfileImage":complaint_profile.profileImage.url if complaint_profile.profileImage else "no image",
                            "speciality":complaint_profile.contact.speciality,
                            "location":complaint_profile.contact.current_job_location
                            }
                
                serializer1.update(case_profile)

                discussion=Discussions.objects.select_related('case','profile').filter(case_id__id=complaint.id)
                if user.id != complaint_profile.contact.userdetail.id:
                    follow=complaint_profile.follow.filter(id=user.id).exists()
                else:
                    follow="uploader"
               
                like=complaint.likes.filter(id=user.id)
                bookmark=complaint.bookmark.filter(id=user.id)
                serializer1['bookmark_status']=bookmark.exists()
                serializer1['bookmark_count']=complaint.bookmark.count()
                serializer1['like_status']=like.exists()
                serializer1['like_count']=complaint.likes.count()
                serializer1['discussion']=discussion.count()
                serializer1['follow']=str(follow)
                serializer1['poll_status']=bookmark.exists()
                serializer1['art_status']=bookmark.exists()
                serializer1["SS_NEET"]= False
                serializer1["PG_NEET"]= False 
                serializer1["newsartical"]= False 
                

                response[datetime.now()]=serializer1
            except Exception as e:
                pass
           
            
                
            try:
                artical=Articals.objects.select_related("user"). filter(created_date=requestpage.object_list[i]['created_date']).prefetch_related("likes","bookmark").get()
                serializer2=ArticalSerializers(artical,many=False).data
               
                artical_profile=Profile.objects.select_related("contact__userdetail").get(contact__userdetail__id=artical.user.id)
                case_profile={
                                "userid":artical.user.id,
                                "ProfileName":artical_profile.contact.profile_name,
                                "ProfileImage":artical_profile.profileImage.url if artical_profile.profileImage else "no image",
                                "speciality":artical_profile.contact.speciality,
                                "location":artical_profile.contact.current_job_location
                            }
                serializer2.update(case_profile)

                if user.id != artical_profile.contact.userdetail.id:
                    follow=artical_profile.follow.filter(id=user.id).exists()
                else:
                    follow="uploader"

                artical_comment=artical.articalcomment_set.all().count()
                
                like=artical.likes.filter(id=user.id)
                bookmark=artical.bookmark.filter(id=user.id)
                serializer2["SS_NEET"]= False
                serializer2["PG_NEET"]= False 
                serializer2["complaint_status"]= False
                serializer2["poll_status"]= False 
                serializer2["discussion"]= artical_comment
                serializer2["follow"]= str(follow)
                serializer2["like_count"]= artical.likes.count()
                serializer2["like_status"]= like.exists()
                serializer2["art_status"]=True
                serializer2["bookmark_status"]= bookmark.exists()
                serializer2["bookmark_count"]= artical.bookmark.all().count()
                serializer2["newsartical"]= False
                
                response[datetime.now()]=serializer2
            except Exception as e:
                pass
           
                
            try:
                question=Question.objects.get(created_date=requestpage.object_list[i]['created_date'])
                serializer=QuestionSerializers(question,many=False).data
                serializer["ProfileImage"]=question.ProfileImage.url if question.ProfileImage  else "no image"
                serializer["complaint_status"]=False 
                serializer["poll_status"]=False 
                serializer["art_status"]=False 
                serializer["SS_NEET"]=True if question.exam=="SS-NEET" else False
                serializer["PG_NEET"]=True if question.exam=="PG-NEET" else False 
                serializer["newsartical"]= False
                try:
                    attemptquestion=question.atteptquestion_set.get(user=user,question=question) 
                    serializer['selected_option']=attemptquestion.selected_option
                    serializer['answer_status']=attemptquestion.answer_status
                except Exception as e:
                    serializer['selected_option']=None
                    serializer['answer_status']=False
                response[datetime.now()]=serializer
            except Exception as e:
                pass
            
                
            
            try:
                artical=NewsArticalPost.objects.select_related("userid").filter(created_date=requestpage.object_list[i]['created_date']).prefetch_related("likes","bookmark").get()
                serializer=NewsArticalSerializers(artical,many=False).data
                profile=Profile.objects.select_related('contact__userdetail').get(contact__userdetail__id=artical.userid.id)
                serializer["ProfileName"]=profile.contact.profile_name
                serializer["ProfileImage"]=profile.profileImage.url if profile.profileImage else "no image"
                serializer["speciality"]=profile.contact.speciality if profile.contact.speciality is not None else "notfilled"
                serializer["location"]=profile.contact.current_job_location
                serializer["bookmark_status"]=artical.bookmark.filter(id=user.id).exists()
                serializer["bookmark_count"]=artical.bookmark.all().count()
                serializer["like_status"]=artical.likes.filter(id=user.id).exists()
                serializer["like_count"]=artical.likes.all().count()
                serializer["follow"]=profile.follow.filter(id=user.id).exists()
                   
               
                serializer["complaint_status"]=False 
                serializer["poll_status"]=False 
                serializer["art_status"]=False 
                serializer["SS_NEET"]= False
                serializer["PG_NEET"]= False 
                serializer["newsartical"]= True
                response[datetime.now()]=serializer
            except Exception as e:
                pass
           
        return Response(response.values())



            
        



 






""" ########################JOB SEARCH API START ##########################"""


       

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
            
            deparments.sort()
            for i in range(len(deparments)):
                
                response[i]={
                    "id":i+1,
                    "department":deparments[i],
                
                }
            return Response(response.values(),status=200)


"""JOB SEARCH BY LOCATION DEPARTMENT DESIGNATION"""

class SearchLocationDepartment(APIView):
    def get(self,request,format=None):
        resp={}
        multilocation=request.GET.get('location').split(",") 
       
        multidepartment=request.GET.get('department').split(",") 
       
        

        username_id=request.GET.get('user_id')
        """USER FIND"""
        user=get_object_or_404(User,id=username_id)
        
        """USER QUERY """
        
       
        if ("" not in multilocation) and ("" not in multidepartment):
            user_query=Q(
                            Q(
                                job_status=True,
                                location__in=multilocation,
                                Speciality__in=multidepartment
                                
                            ) 
                        )
            
        elif "" not in multilocation:
            user_query=Q(job_status=True,location__in=multilocation)                    
                  
        elif "" not in multidepartment:
            user_query=Q(Speciality__in=multidepartment,job_status=True) 
            
        else:
            return Response(resp.values(),status=200)
         
       
        """GETING JOBS HERE BASED ON USER QUERY"""
        jobs=Category_Related_Job.objects.filter(user_query).order_by('-created_date')
       
        """GETING SINGLE JOB AND BINDING BOOKMARK,LIKE,APPLY"""           
        for job in jobs:

            serializer=Category_Related_JobSerializers(job,many=False).data
            serializer['eligibility']=[ {"name":i} for i in job.qualification.split(",")]
            serializer["bookmark_status"]=job.bookmark.filter(id=user.id).exists()
            serializer["like_status"]=job.likes.filter(id=user.id).exists()
            serializer["apply_status"]=job.applicant.filter(id=user.id).exists()
            resp[job.id]=serializer  
        return Response(resp.values(),status=200)
        

"""END JOB SEARCH API"""

###################START QUESTION AND ANSWER PART#############################
class GetQuestion(APIView):
    def get(self,request):
        question=request.GET.get('id')
        examination=request.GET.get('exam')
        userid=request.GET.get('user_id')

        response={}
        try:
            user=User.objects.get(id=userid)
        except Exception as e:
            return Response({"message":"user id not found","status":False},status=status.HTTP_400_BAD_REQUEST)
        
        if question is not None:
            
            serializer=QuestionSerializers(Question.objects.get(id=question),many=False)
            serializer["ProfileImage"]=question.ProfileImage.url if question.ProfileImage  else "no image"
            serializer["poll_status"]=False
            serializer["art_status"]=False
            serializer['PG_NEET']=True if question.exam=="PG-NEET" else False
            serializer['SS_NEET']=True if question.exam=="SS-NEET" else False
            serializer["complaint_status"]=False
            serializer["newsartical"]=False
            try:
                attemptquestion=question.atteptquestion_set.get(user=user,question=question) 
                serializer['selected_option']=attemptquestion.selected_option
                serializer['answer_status']=attemptquestion.answer_status
            except Exception as e:
                serializer['selected_option']=None
                serializer['answer_status']=False
            return Response(serializer.data)
        
        elif examination is not None:
            questions=Question.objects.filter(exam__iexact=examination).order_by('-created_date')
            for question in questions:
                serializer=QuestionSerializers(question,many=False).data
                serializer["ProfileImage"]=question.ProfileImage.url if question.ProfileImage  else "no image"
                serializer["poll_status"]=False
                serializer["art_status"]=False
                serializer['PG_NEET']=True if question.exam=="PG-NEET" else False
                serializer['SS_NEET']=True if question.exam=="SS-NEET" else False
                serializer["complaint_status"]=False 
                serializer["newsartical"]=False 
                try:
                    attemptquestion=question.atteptquestion_set.get(user=user,question=question) 
                    serializer['selected_option']=attemptquestion.selected_option
                    serializer['answer_status']=attemptquestion.answer_status
                except Exception as e:
                    serializer['selected_option']=None
                    serializer['answer_status']=False
                response[question.id]=serializer
            return Response(response.values())

        
        
        # else:
        #     serializer=QuestionSerializers(Question.objects.all().order_by("-created_date"),many=True)
        #     return Response(serializer.data)



class AttemptQuestions(APIView):
    def get(self,request):
        userid=request.GET.get('user_id')
        response={}
        try:
            user=User.objects.get(id=userid)
        except Exception as e:
            return Response ({"message":"user id not found","staus":False,"error":str(e)},status=status.HTTP_400_BAD_REQUEST)

        attempt_question=user.atteptquestion_set.all()
        for i in attempt_question:
            serializers=AtteptQuestionSerializers(i,many=False).data
            serializers['question']=i.question.question
            response[i.id]=serializers
        return Response(response.values(),status=status.HTTP_200_OK)
    
    def post(self,request):
        if not request.POST._mutable:
            request.POST._mutable = True
        data=request.data
        
        serializers=AtteptQuestionSerializers(data=data)
        user=get_object_or_404(User,id=data['user'])
        data['user']=user.id
        question=get_object_or_404(Question,id=data['question'])

        if AtteptQuestion.objects.filter(user=user,question=question).exists():
            return Response({"message":"you already attempted this question","status":True})
        
        data['question']=question.id
        optionlist=["A","B","C",'D']
        if data['selected_option'] not in optionlist:
            return Response({"message":"this is not valid option","status":False},status=status.HTTP_400_BAD_REQUEST)
        
        elif data['selected_option']==question.correct_answer:
            data['answer_status']=True
        
        
        if serializers.is_valid():
            serializers.save()
            serializer=serializers.data
            serializer['correct_answer']=question.correct_answer
            return Response(serializer)
        else:
            return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)

class HospitlMultiimage(APIView):
    
    def get(self,request):
        jobid=request.GET.get('jobid')
        hospitalimage=HospitlMultiimage.objects.filter(job__id=jobid)
        pass 
    

class BannerMultiimage(APIView):
    
    def get(self,request):
        serializers=BannerSerializer(Banner.objects.all(),many=True)
        return Response(serializers.data)
    



