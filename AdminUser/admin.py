from django.contrib import admin

from AdminUser.models import NewsPages, Pages
from AdminUser.serializers import NewsPagesSerializers

# Register your models here.
admin.site.register(Pages)
admin.site.register(NewsPages)