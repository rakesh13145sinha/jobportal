from distutils.command.upload import upload
from django.db import models

# Create your models here.
RelatedField=[('Medical','Medical'),('Enginnering','Enginnering')]
Lavel=[('State','State'),('National','National'),('Institute','Institute')]
class Examination(models.Model):
	name=models.CharField(max_length=100)
	level_of_exam=models.CharField(max_length=50,null=True,choices=Lavel)
	related_exam=models.CharField(max_length=100,choices=RelatedField)#Medical Enginnering
	created=models.DateTimeField(auto_now=True,auto_now_add=False)

	def __str__(self):
		return "%s %s" %(self.name,self.related_exam)




class Course(models.Model):
	entrance=models.ForeignKey(Examination,on_delete=models.DO_NOTHING,null=True)
	name=models.CharField(max_length=100)
	duration=models.IntegerField()
	related_field=models.CharField(max_length=100,choices=RelatedField)#Medical Enginnering
	created=models.DateTimeField(auto_now=True,auto_now_add=False)

	def __str__(self):
		return "%s %s" %(self.name,self.related_field)



AUTONOUS=[('Yes','Yes'),('No','No')]
PROPERTIES=[('Privete','Private'),('Government','Government'),('Semi-Government','Semi-Government')]
class MedicalCollege(models.Model):
	name=models.CharField(max_length=200)
	sortname=models.CharField(max_length=50,null=True)
	approved=models.CharField(max_length=200)
	level=models.CharField(max_length=50)#National level or State level
	state_ranking=models.IntegerField()
	national_ranking=models.IntegerField()
	branch=models.IntegerField()#total branch in college
	sit=models.IntegerField()#total site
	establishment=models.DateField()
	staff=models.IntegerField(null=True)
	autonomus=models.CharField(max_length=5,choices=AUTONOUS)#yes or no
	university=models.CharField(max_length=100)
	image=models.ImageField(upload_to='college/image')
	about_college=models.TextField()
	properties=models.CharField(max_length=30,choices=PROPERTIES,null=True)
	last_year_rank=models.IntegerField(null=True)
	available_course=models.ManyToManyField(Course,related_name='course')
	entrance_exam=models.ManyToManyField(Examination,related_name='entrance')
	cutoff=models.IntegerField(null=True)
	annual_free=models.IntegerField(null=True)
	city=models.CharField(max_length=100)
	district=models.CharField(max_length=100)
	state=models.CharField(max_length=50)
	landmark=models.CharField(max_length=100)
	postal_address=models.CharField(max_length=200)
	pincode=models.IntegerField()



	def __str__(self):
		return '%s %s %s' %(self.sortname,self.properties,self.state)

class Report(models.Model):
	name=models.CharField(max_length=20)
	image=models.ImageField(upload_to='college/image')