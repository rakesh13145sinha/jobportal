from django.contrib import admin
from .models import *


class Job_By_CategoryAdmin(admin.ModelAdmin):
	list_display=['id','title']
	list_editable=['title']

class Category_Related_JobAdmin(admin.ModelAdmin):
	# list_filter=['location','Speciality','category']
	list_display=['id','category','Speciality','job_status']
	list_editable=['job_status','Speciality']


class PollAdmin(admin.ModelAdmin):
	list_display=['id','option1']

class NewsArticalPostAdmin(admin.ModelAdmin):
	list_display=['id']

class ComplaintAdmin(admin.ModelAdmin):
	list_display=['id']


class MultiImageAdmin(admin.ModelAdmin):
	list_display=['id','complaint','news_poll']

class ProfileAdmin(admin.ModelAdmin):
	list_display=['id','contact',]

class IdentificationAdmin(admin.ModelAdmin):
	list_display=['id','phone_number','userdetail',]


class Doctor_SpecialistAdmin(admin.ModelAdmin):
	list_display=['id','name','status',]
	list_editable=['name',]

class SaveOtpAdmin(admin.ModelAdmin):
	list_display=['phone_number','otp',]
	



admin.site.register(Identification,IdentificationAdmin)
admin.site.register(Profile,ProfileAdmin)
admin.site.register(Category_Related_Job,Category_Related_JobAdmin)
admin.site.register(Job_By_Category,Job_By_CategoryAdmin)
admin.site.register(HigherQualification)
admin.site.register(Complaint,ComplaintAdmin)
admin.site.register(Designation)
admin.site.register(Experience)
admin.site.register(State)
admin.site.register(City)
admin.site.register(SaveOtp,SaveOtpAdmin)
admin.site.register(Poll,PollAdmin)
admin.site.register(College_Story)
admin.site.register(Articals)
admin.site.register(PollVote)
admin.site.register(Discussions)
admin.site.register(ResumeUpload)
admin.site.register(HospitalInfo)



