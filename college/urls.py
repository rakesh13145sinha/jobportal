from django.urls import path,include
from college.views import * 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
	path('info/',include([
			path('get/',AllCollege.as_view(),name="get_all_college"),
			path('exam',EnteranceExam.as_view())

		]))



]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
