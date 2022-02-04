from django.urls import path
from django.urls.conf import include
from .views import *
urlpatterns=[
    path('login',Admin_Login.as_view()),
   
    path('category/',include([

        path('post',Job_Category_Post.as_view()),
        path('jobs/',JobCategorybyid.as_view()),
        path('deleted/jobs',DeletedJobs.as_view()),
        path('jobs/total',Total_Active_Jobs.as_view()),
        
    ])),
   
    path('page/',include([

        path('post',Page.as_view()),
        path('news/post',NewsPagePost.as_view()),
        path('like',PageNewsLike.as_view()),
        path('bookmark',PageNewsBookmark.as_view()),
        
    ])),
    path('dropdownlist/',include([
        path('speciality_department',Speciality_And_Department.as_view()),
        path('state',Show_State.as_view())
    ])),
    path("user/",include([ 
        path('detail',UserProfile.as_view())
    ])),
    path('create/',include([
        path('higher/qualifcation',Add_Qualification.as_view()),
        path('hospital/type',Add_Hospital_Type.as_view()),
        path('department',Add_Spec_Department.as_view()),
        path('designation',Add_Designation.as_view()),
       

    ]))
    


]