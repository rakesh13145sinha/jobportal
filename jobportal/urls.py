
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.schemas import get_schema_view
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Doctor worker API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.doctorwork.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="Test License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('job.urls')),
    path('api/college/',include('college.urls')),
    path('api/comment/',include('comment.urls')),
    path('api/admin/',include('AdminUser.urls')),
    path('', schema_view.with_ui('swagger',), name='schema-swagger-ui') ,
    path('doc',schema_view.with_ui('redoc',), name='schema-redoc')
    
   
]
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns+=static(settings.STATIC_ROOT, document_root=settings.MEDIA_ROOT)