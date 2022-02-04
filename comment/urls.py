from django.urls import path,include
from comment.views import * 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
	path('question/',include([
			path('post/',QuestionSubmit.as_view(),name="question_post"),
			path('like/',QuestionLike.as_view(),name="question_like"),

		])),

	path('answer/',include([
			path('post/',AnswerSubmit.as_view(),name="answer_post"),
			path('like/',AnswerLike.as_view(),name="answer_like"),

			
		]))

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
