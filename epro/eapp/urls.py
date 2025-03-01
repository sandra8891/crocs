from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)