from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField,ProcessedImageField
from datetime import *
from imagekit.processors import ResizeToFill

# Create your models here.
class Identification(models.Model):
    userdetail=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    phone_number=models.CharField(max_length=20,null=True)
    profile_name=models.CharField(max_length=50,null=True)
    current_job_location=models.CharField(max_length=100,null=True)
    speciality=models.CharField(max_length=255,null=True)
    hightest_qualification=models.CharField(max_length=255,null=True)
    status=models.BooleanField(default=False)


    class Meta:
        unique_together = ('phone_number','userdetail')
    def __str__(self):
        return self.phone_number 
    
    # def save(self,*args,**kwargs):
    #     self.status=True
    #     super(Identification,self).save(*args,**kwargs)
  
class Profile(models.Model):
    contact=models.ForeignKey(Identification,on_delete=models.CASCADE,null=True)
    
    profileImage=models.ImageField(upload_to='profile/image',null=True,blank=True)
    current_department=models.CharField(max_length=100,null=True)
    current_institute=models.CharField(max_length=100,null=True)
    
    dob=models.DateField(null=True,blank=True)
    gender=models.CharField(max_length=50,null=True,blank=True)
    language=models.CharField(max_length=100,null=True)
    
    degrees=models.CharField(max_length=100,null=True)#In which field you finish graduation and pg
    ug=models.CharField(max_length=100,null=True)
    ug_institute_name=models.CharField(max_length=100,null=True)
    pg=models.CharField(max_length=100,null=True)
    pg_institute_name=models.CharField(max_length=100,null=True)
    
    skill=models.TextField(null=True)
    tell_me_about_youself=models.TextField(null=True)
    
    
    follow=models.ManyToManyField(User,related_name="follow")
    status=models.BooleanField(default=False,null=True)
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    updated_date=models.DateTimeField(auto_now=True,auto_now_add=False,null=True)

    class Meta:
        unique_together = ('contact',)
    # def __str__(self):
    #     return self.contact
    
    # def save(self,*args,**kwargs):
    #     self.status=True
    #     super(Profile,self).save(*args,**kwargs)




    # class Meta:
    #     unique_together = ('phone_number',)
    # def __str__(self):
    #     return self.phone_number
    
    # def save(self,*args,**kwargs):
    #     self.status=True
    #     super(Identification,self).save(*args,**kwargs)
    



class SaveOtp(models.Model):
    phone_number=models.CharField(max_length=20,unique=True)
    otp=models.CharField(max_length=5)
    
    def __str__(self):
        return self.phone_number

class ResumeUpload(models.Model):
    userid=models.ForeignKey(User,on_delete=models.CASCADE)
    upload_file=models.FileField(upload_to="resume")
    status=models.BooleanField(default=False)
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True) 

    def save(self,*args,**kwargs):
        self.status=True 
        super(ResumeUpload,self).save(*args,**kwargs)

class Experience(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    hospital_name=models.CharField(max_length=100)
    designation=models.CharField(max_length=100)
    department=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    start_date= models.DateField()
    end_date= models.CharField(max_length=50,null=True)


    


    



class Subject(models.Model):
    #image=models.ImageField(upload_to='subject',null=True,blank=True)
    image=ProcessedImageField(upload_to='subject',
                                           processors=[ResizeToFill(150,150)],
                                           format='JPEG',
                                           options={'quality': 20},null=True,blank=True)
    
    name=models.CharField(max_length=100)
    status=models.BooleanField(default=True)
    class Meta:
        unique_together=('name',)
    def __str__(self):
        return self.name


class Job_By_Category(models.Model):
    #THIS IS NOT RELATED TO BACKENCKEND 
    title=models.CharField(max_length=200)
    about=models.CharField(max_length=200,null=True,blank=True)

    image=models.ImageField(upload_to='job_title',null=True,blank=True)
    
    category_status=models.BooleanField(default=True)

    class Meta:
        unique_together = ('title',)
    def __str__(self):
        return self.title

class HospitalInfo(models.Model):
    name=models.CharField(max_length=200,null=True)
    typeofhospital=models.CharField(max_length=200,null=True)
    city=models.CharField(max_length=200,null=True)
    location=models.CharField(max_length=200,null=True)
    state=models.CharField(max_length=200,null=True)
    no_of_OT=models.CharField(max_length=200,null=True)
    no_of_sepeciality=models.CharField(max_length=200)
    no_of_bed=models.CharField(max_length=200)
    daily_OPD=models.CharField(max_length=200)
    icu=models.IntegerField(null=True)
    nicuc=models.IntegerField(null=True)    
    picu=models.IntegerField(null=True)

    def __str__(self):
        return self.name
        
class HospitalBanner(models.Model):
    hospital=models.ForeignKey(HospitalInfo,on_delete=models.CASCADE,null=True)
    file=models.FileField(upload_to='hostpital/image',null=True)

class HospitalHighlight(models.Model):
    hospital=models.ForeignKey(HospitalInfo,on_delete=models.CASCADE,null=True)
    title=models.CharField(max_length=200)
    file=models.FileField(upload_to='hostpital/image',null=True)

class HospitalSpeciality(models.Model):
    hospital=models.ForeignKey(HospitalInfo,on_delete=models.CASCADE,null=True)
    title=models.CharField(max_length=200)
    file=models.FileField(upload_to='hostpital/image',null=True)

YEAR_OR_MONTHLY_SALAY = [
        ('Monthly', 'MONTHLY'),
        ('Anual', 'ANNUAL'),
        
    ]
GENDER = [
        ('Female', 'FEMALE'),
        ('Male', 'MALE'),
        ('Male/Female','MALE/FEMALE')
        
    ]


JOBTYPE=[("Part Time","Part Time"),("Full Time","Full Time")]

class Category_Related_Job(models.Model):
    category=models.ForeignKey(Job_By_Category,on_delete=models.CASCADE)
    Speciality=models.CharField("consultent speciality",max_length=500,null=True)
    designation=models.CharField(max_length=100,null=True,db_column='consultent Designation')
    hosptial_name=models.CharField('Hospital name',max_length=500,null=True,blank=True,)
    hospitail_image=ProcessedImageField(upload_to='Hospital image',
                                           processors=[ResizeToFill(150,150)],
                                           format='JPEG',
                                           options={'quality': 20},null=True,blank=True)
    location=models.CharField('Job Location',max_length=100,null=True)
    #state=models.CharField("Job State",null=True,max_length=200)
    salary=models.CharField(max_length=250,null=True)
    monthly_or_anual=models.CharField("Monthly/Annual",max_length=100,choices=YEAR_OR_MONTHLY_SALAY,default='Monthly',null=True)
    experince=models.CharField(max_length=250,null=True)
    gender=models.CharField(" Gender preference",max_length=20,choices=GENDER,default="Male",)
    qualification=models.CharField(max_length=500)
    vacancy=models.IntegerField()
    working_hours=models.CharField("Working Hours",max_length=100)
    working_day=models.CharField("Woking Day",max_length=100)
    discription=models.TextField("Role And Responsibility")
    accommodation=models.CharField(max_length=20)
    hospital_type=models.CharField(max_length=100,null=True)
    job_type=models.CharField(max_length=100,null=True,choices=JOBTYPE)
    
    hr_contact=models.CharField(max_length=20,null=True,default="1234567890")
    social_contact=models.CharField(max_length=20,null=True,default="0123456789")
    top_job=models.BooleanField(default=False)
    job_status=models.BooleanField(default=True)
    resion=models.CharField(max_length=2000,null=True,blank=True)
    likes=models.ManyToManyField(User,related_name="like",)
    bookmark=models.ManyToManyField(User,related_name="bookmarks",)
    applicant=models.ManyToManyField(User,related_name="application")
    post_date=models.DateField(null=True)
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    updated_date=models.DateTimeField(auto_now=True,auto_now_add=False)
    def __str__(self):
        return self.Speciality

class NewsArticalPost(models.Model):
    userid=models.ForeignKey(User ,on_delete=models.CASCADE)
    title=models.CharField(max_length=200,null=True)
    image=models.ImageField(upload_to='news/image/',null=True,blank=True)
    discription=models.TextField()
    status=models.BooleanField(default=False) 
    likes=models.ManyToManyField(User,related_name="artical_likes")
    bookmark=models.ManyToManyField(User,related_name="newsartical",default=None,blank=True)

    created_date=models.DateTimeField(auto_now=False,auto_now_add=True)
    update=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    
    def save(self,*args,**kwargs):
        self.artical_status=True
        super(NewsArticalPost, self).save(*args, **kwargs)


class Poll(models.Model):
    poll_user=models.ForeignKey(User ,on_delete=models.CASCADE)
    title=models.CharField(max_length=500,null=True)
    
    image=models.ImageField(upload_to='news/image/',null=True,blank=True)
    option1=models.CharField(max_length=200,null=True)
    option2=models.CharField(max_length=200,null=True)
    option3=models.CharField(max_length=200,null=True)
    option4=models.CharField(max_length=200,null=True)
    poll_status=models.BooleanField(default=False) 
    likes=models.ManyToManyField(User,related_name="poll_likes")
    bookmark=models.ManyToManyField(User,related_name="pollbookmark",default=None,blank=True)
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    update=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    def save(self,*args,**kwargs):
        self.poll_status=True
        super(Poll, self).save(*args, **kwargs)


#this is for poll voter
class PollVote(models.Model):
    OPTIONS=[("A","A"),("B","B"),("C","C"),("D","D")]
    poll=models.ForeignKey(Poll,on_delete=models.CASCADE)
    profile=models.ForeignKey(User,on_delete=models.CASCADE)
    choice=models.CharField(max_length=5,choices=OPTIONS)
    vote=models.BooleanField(default=False) 
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    

    def __str__(self):
        return self.profile.username
    
    def save(self,*args,**kwargs):
        self.vote=True
        super(PollVote,self).save(*args,**kwargs)

#poll comment store in the table
class PollComment(models.Model):
    
    poll=models.ForeignKey(Poll,on_delete=models.CASCADE)
    profile=models.ForeignKey(User,on_delete=models.CASCADE)
    comment=models.TextField()
    agree=models.ManyToManyField(User,related_name="poll_agree")
    disagree=models.ManyToManyField(User,related_name="Poll_disagree")
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)

    def __str__(self):
        return self.profile.username


class College_Story(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    new_story=models.CharField(max_length=200)
    college_name=models.CharField(max_length=100)
    date=models.DateField()
    
    photos=models.ImageField(upload_to='news/image/',null=True)
    discription=models.TextField()
    storydate=models.DateTimeField(auto_now=True,auto_now_add=False,null=True)
    status=models.BooleanField(default=False)
    likes=models.ManyToManyField(User,related_name="college_story_likes")
    bookmark=models.ManyToManyField(User,related_name="college_story_bookmark",default=None,blank=True)
    update=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    def __str__(self):
        return self.new_story


class Articals(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    # mediafile=ProcessedImageField(upload_to='news/image/',
    #                                        processors=[ResizeToFill(150,150)],
    #                                        format='JPEG',
    #                                        options={'quality': 40},null=True)
    image=models.ImageField(upload_to='news/image/',null=True)
    discription=models.TextField()
    likes=models.ManyToManyField(User,related_name="articalslike")
    bookmark=models.ManyToManyField(User,related_name="articalsbookmark")
    status=models.BooleanField(default=True) 
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    update=models.DateTimeField(auto_now=True,auto_now_add=False,null=True)

    # def __str__(self):
    #     return self.artical_title

#this store Artical comment
class ArticalComment(models.Model):
    
    artical=models.ForeignKey(Articals,on_delete=models.CASCADE)
    profile=models.ForeignKey(User,on_delete=models.CASCADE)
    comment=models.TextField()
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)

    def __str__(self):
        return self.profile.username






#NEW CASE POST
class Complaint(models.Model):
    complaint=models.ForeignKey(User ,on_delete=models.CASCADE)
    title=models.CharField(max_length=500,null=True,blank=True)
    image=models.ImageField(upload_to='com/',null=True,blank=True)
    chief_complaint=models.TextField(null=True,blank=True)
    present_illness=models.TextField(null=True,blank=True)
    past_illness=models.TextField(null=True,blank=True)
    drugs=models.CharField(max_length=500,null=True,blank=True)
    personal=models.TextField(null=True,blank=True) 
    family=models.CharField(max_length=500,null=True,blank=True)
    physical_exam=models.TextField(null=True,blank=True) 
    system_exam=models.CharField(max_length=500,null=True,blank=True)
    local_exam=models.CharField(max_length=200,null=True,blank=True)
    vitus=models.CharField(max_length=200,null=True,blank=True)
    lab_finding=models.CharField(max_length=200,null=True,blank=True)
    imaging=models.CharField(max_length=200,null=True,blank=True)
    diagnosis=models.CharField(max_length=500,null=True,blank=True)
    complaint_status=models.BooleanField(default=True)
    likes=models.ManyToManyField(User,related_name="case_likes")
    bookmark=models.ManyToManyField(User,related_name="case_bookmark",default=None,blank=True)
    created_date=models.DateTimeField(auto_now=True,auto_now_add=False,null=True)
    update=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    
    # def __str__(self):
    #     return self.drugs
    
    def save(self,*args,**kwargs):
        self.complaint_status=True
        super(Complaint,self).save(*args,**kwargs)

#it store complaint comment
class Discussions(models.Model):
    
    case=models.ForeignKey(Complaint,on_delete=models.CASCADE)
    profile=models.ForeignKey(User,on_delete=models.CASCADE)
    comment=models.TextField()
    agree=models.ManyToManyField(User,related_name="case_agree")
    disagree=models.ManyToManyField(User,related_name="case_disagree")
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    def __str__(self):
        return self.profile.username
    




"""specialist"""
class Hospital_Department(models.Model):
    department_name=models.CharField(max_length=200)
    class Meta: 
        unique_together=('department_name',)
    
    def __str__(self):
        return self.department_name

class Designation(models.Model):
    #department=models.ForeignKey(Hospital_Department,on_delete=models.CASCADE,null=True)
    position=models.CharField(max_length=200)
    
    def __str__(self):
        return self.position

class Hospital_Type(models.Model):
    hospitaltype=models.CharField(max_length=200)
    class Meta:
        unique_together=('hospitaltype',)
    
    def __str__(self):
        return self.hospitaltype

class HigherQualification(models.Model):
    qualification=models.CharField(max_length=200,unique=True)
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True)
    
    def __str__(self):
        return self.qualification

class Salary(models.Model):
    min_salary=models.FloatField()
   
    class Meta:
        unique_together=('min_salary',)
    
    
class Experince(models.Model):
    min_experince=models.CharField(max_length=20,null=True)
    class Meta:
        unique_together=('min_experince',)
    
    
class Accommodation(models.Model):
    accommodation=models.CharField(max_length=100)
    class Meta:
        unique_together=('accommodation',)
    
    def __str__(self):
        return self.accommodation

class State(models.Model):
    name=models.CharField(max_length=100)
    status=models.BooleanField(default=True)
    created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class City(models.Model):
    state=models.ForeignKey(State,on_delete=models.CASCADE,null=True)
    hospital_city_name=models.CharField(max_length=100,db_column="city")
    class Meta:
        unique_together=('hospital_city_name',)
    def __str__(self):
        return self.hospital_city_name




    
