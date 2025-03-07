from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views

urlpatterns = [
    path('login', views.loginuser, name='loginuser'),
    path('adminindex', views.adminindex, name='adminindex'),  
    path('usersignup', views.usersignup, name='usersignup'),
    path('forgotpassword',views.getusername,name='forgotpassword'),
    path('verifyotp',views.verifyotp,name='verifyotp'),
    path('gallery',views.gallery,name='gallery'),
    path('passwordreset',views.passwordreset,name='passwordreset'),
    path('logout', views.logoutuser, name="logoutuser"),
    path('',views.firstpage,name="firstpage"), 
    path('products/<int:id>',views.products,name='products'),
    path('addtocart/<int:id>/', views.addtocart, name='addtocart'),
    path('cview/', views.cview, name='cview'),
    path('about_us/',views.about_us,name='about_us'),
    path('home',views.home,name='home'),
    path('adminlogout',views.logoutadmin,name="adminlogout"),
    path('deletion/<int:id>/', views.delete_g, name='deletion'),
    path('edit/<int:pk>/', views.edit_g, name='edit_g'),

   
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


