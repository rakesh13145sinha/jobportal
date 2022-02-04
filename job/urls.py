from django.urls import path,include
from .views import *
urlpatterns=[
        
    path('auth/',include([
                
                path('otp',Validate_OTP.as_view()),
                path('resend/otp/',Resend_otp.as_view()),
                path('logout/',Logout.as_view()),
                path('follow/',TryToFollowUnfollow.as_view()),
                path('following/',FollowingProfile.as_view()),
                path('upload/file/',UserResumeUpload.as_view(),name="resume upload"),
                path('registration',UserRegistration.as_view())
                
                ])),
    
    path('new/job/',New_Job_Post.as_view()),
    path('subject/',Subjects.as_view()),
    path('user/',include([
              
                path('personal/info',UpdatePersonalInfo.as_view()),
            
                path('add/exp',UserExperience.as_view()),
                path('profession/info',ProfessionalInfo.as_view()),
                path('profession/ug', Under_Graduation_Degree_List.as_view()),
                path('profession/ug/institute', Under_Graduation_Degree_insttute_List.as_view()),
                path('profession/pg/', Post_Graduation_Degree_List.as_view()),
                path('profession/pg/institute', Post_Graduation_Degree_institute_List.as_view()),
                path('profession/hospital/department', Specility_Department_list.as_view()),
                path('profession/hospital/type', Hospital_Type_Lists.as_view()),
                path('profession/language', Languages.as_view()),
                path('profession/gender', Gender.as_view()),
                
                

                path('case',User_Posted_Case.as_view()),
                path('case/bookmarks',User_Bookmark_Case.as_view()),
                path('case/likes',User_Like_Case.as_view()),
                path('news',User_Posted_News.as_view()),
                path('news/bookmarks',User_News_Bookmarks.as_view()),
                path('news/likes',User_News_LIke.as_view()),
                path('artical/post',User_Posted_Artical.as_view()),
                path('artical/likes',User_Artical_LIke.as_view()),
                path('artical/bookmarks',User_Artical_Bookmarks.as_view()),
                path('college/story',User_College_Story_Posted.as_view()),
                path('college/story/likes',User_College_Story_LIke.as_view()),
                path('college/story/bookmarks',User_College_Stroy_Bookmarks.as_view()),
                path('poll',User_Poll_Posted.as_view()),
                path('poll/likes',User_Poll_LIke.as_view()),
                path('poll/bookmarks',User_Poll_Bookmarks.as_view())
               

                    ])),
   
    path('ios/',include([
                    path('user/profile/',User_Profile_In_Ios_System.as_view()),
                    path('artical',ArticalPost_ios.as_view()),
                    path('college/story',CollegeStoryPost.as_view()),
                    path('poll',PollPost.as_view()),
                    path('case',ComplaintPost.as_view()),
                    

                    ])),
    
    
    path('job/',include([
                        path('like/',Likes.as_view()),
                        path('bookmark/',BookMark.as_view()),
                        path('apply/',Jobs_Applies.as_view()),
                        path('department/',Department_By_Job.as_view(),name="department and speciality both same"),
                        path('location/',Location_By_job_search.as_view(),name="show_job_count_related_to_location"),
                        path('designations/',All_Designations.as_view()),
                        
                        path('search/higher/qualifiction',DoctorHigherQualification.as_view()),
                        path('search/state',State_Location.as_view()),
                        path('search/state/location',City_Location.as_view()),
                      
                        path('search/result',SearchResult.as_view()),
                       
                        path('profile/',User_Profile.as_view()),
                        path('category/',New_Job_Category_Post.as_view()),
                        path('news/category/',News_Category.as_view(),name="news_category"),
                        path('news/category/artical/',Related_TO_News_Category.as_view()),
                        path('post/',JobRequestPost.as_view(),name="request_for_job_post"),
                        path('top/',TopJob.as_view(),name="top_jobs"),
                        path('search/',Search_Location_Department_Designation.as_view()),
                        #test part for search data store in file
                        path('search/recent',Recent_Search.as_view()),
                        path('all',All_Jobs.as_view())
                        ])),
    
    path('news/',include([
                    path('artical/post/',News_Artical_Post.as_view(),name="news_articalpost"),
                    path('artical/post',NewsArticalPost_Ios.as_view()),#IOS 
                    path('poll/post/',News_Poll.as_view(),name="poll"),
                    path('poll/vote/',VoteForPoll.as_view(),name="caste vote"),
                    path('poll/comment/',Poll_Comment.as_view(),name="poll_comment"),
                    path('college/story/',College_Storires.as_view(),name="new_college_story"),
                    path('artical/',ArticalPost.as_view(),name="artical_post"),
                    path('artical/comment/',Artical_Comment.as_view(),name='artical_comment'),
                    path('multi_image/post/',Multi_Image_Post.as_view(),name="multiple_image"),
                    path('poll/complaint/',ComplaintAndPoll.as_view(),name="get_poll_complaint"),
                  
                   
                   
                        ])),
    
    path('complaint/',include([
                path('',Complaint_Post.as_view(),name='complaint'),
                path('comment/',Complaint_Comment.as_view(),name='comment'),
               

        ])),
    path('custom/',include([
                    path('user/',User_Customize_Jobs.as_view(),name='custome_jobs')
                        ])),
    path('banner/',include([path('job/',Job_Banner.as_view()),
                            path('promotional/',Promotional_Banner.as_view()),

                        ])),
    path('upload/',include([

                path('status/',Upload_status.as_view()),
               
                ])),
    
    
]