from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.core.mail import send_mail
from django.conf import settings
import random
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from .models import *






def gallery(request):
    if request.method == 'POST' and 'image' in request.FILES: 
        myimage = request.FILES['image']  
        todo123=request.POST.get("todo")
        todo321=request.POST.get("date")
        todo311=request.POST.get("course")  
        obj=Gallery(title1=todo123,title2=todo321,title3=todo311,feedimage=myimage,user=request.user)
        obj.save()
        data=Gallery.objects.all()
        return redirect('adminindex')
    
    gallery_images = Gallery.objects.all()
    return render(request, "galleryupload.html")

def usersignup(request):
    if request.POST:
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confpassword')

        
        if not username or not email or not password or not confirmpassword:
            messages.error(request, 'All fields are required.')
        elif confirmpassword != password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
        
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully!")
            return redirect('loginuser')  

    return render(request, "signup.html")

def loginuser(request):
    if request.user.is_authenticated:
        return redirect('firstpage')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['username'] = username
            if  user.is_superuser:
                return redirect('adminindex')
            else:
                return redirect('firstpage')
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'login.html')

def adminindex(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access this page.")
        return redirect('loginuser')

    data = Gallery.objects.all()
    gallery_images = Gallery.objects.filter(user=request.user)
    return render(request, 'adminindex.html', {"gallery_images": gallery_images})



def firstpage(request): 
    return render(request, "userindex.html")



def verifyotp(request):
    if request.POST:
        otp = request.POST.get('otp')
        otp1 = request.session.get('otp')
        otp_time_str = request.session.get('otp_time') 

    
        if otp_time_str:
            otp_time = datetime.fromisoformat(otp_time_str)
            otp_expiry_time = otp_time + timedelta(minutes=5)
            if datetime.now() > otp_expiry_time:
                messages.error(request, 'OTP has expired. Please request a new one.')
                del request.session['otp']
                del request.session['otp_time']
                return redirect('verifyotp')

        if otp == otp1:
            del request.session['otp']
            del request.session['otp_time']
            return redirect('passwordreset')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    
    otp = ''.join(random.choices('123456789', k=6))
    request.session['otp'] = otp
    request.session['otp_time'] = datetime.now().isoformat()
    message = f'Your email verification code is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [request.session.get('email')]
    send_mail('Email Verification', message, email_from, recipient_list)

    return render(request, "otp.html")

def delete_g(request,id):
    feeds=Gallery.objects.filter(pk=id)
    feeds.delete()
    return redirect('index')

def edit_g(request, pk):
    gallery_item = Gallery.objects.filter(pk=pk).first()

    if not gallery_item:
        messages.error(request, "Gallery item not found.")
        return redirect('index')

    if request.method == "POST":
        edit1 = request.POST.get('todo')
        edit2 = request.POST.get('date')
        edit3 = request.POST.get('course')


        gallery_item.title1 = edit1
        gallery_item.title2 = edit2
        gallery_item.title3 = edit3

        if 'image' in request.FILES:
            gallery_item.feedimage = request.FILES['image']

        gallery_item.save()

        messages.success(request, "Gallery item updated successfully.")
        return redirect('index')

    else:
        return render(request, 'edit_gallery.html', {'data': gallery_item})





def getusername(request):
    if request.POST:
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            request.session['email'] = user.email
            return redirect('verifyotp')
        except User.DoesNotExist:
            messages.error(request, "Username does not exist.")
            return redirect('getusername')

    return render(request, 'getusername.html')


def passwordreset(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confpassword')

    
        if confirmpassword != password:
            messages.error(request, "Passwords do not match.")
        else:
            email = request.session.get('email')
            try:
                user = User.objects.get(email=email)

                user.set_password(password)
                user.save()

                del request.session['email']
                messages.success(request, "Your password has been reset successfully.")
                
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)

                return redirect('loginuser')
            except User.DoesNotExist:
                messages.error(request, "No user found with that email address.")
                return redirect('getusername')

    return render(request, "passwordreset.html")


def products(request,id):
    gallery_images =Gallery.objects.filter(pk=id)
    return render(request,'products.html',{"gallery_images": gallery_images})

def cview(request):
    if request.user.is_authenticated:
        citems = Cart.objects.filter(user=request.user)
        cart_item_count = citems.count()  # Get the count of items in the cart
        return render(request, 'cart.html', {"citems": citems, "cart_item_count": cart_item_count})
    else:
        return redirect('loginuser')


def addtocart(request, id):
    if request.user.is_authenticated:
        product = Gallery.objects.get(id=id)
        citems, created = Cart.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            print(f"Cart Item Added: {product.title1}")
        else:
            print(f"Cart Item already in cart: {product.title1}")
        
        return redirect('cview') 
    else:
        return redirect('loginuser') 

def about_us(request):
    return render(request,'aboutus.html')
def home(request):
    return render(request,'userindex.html')

def logoutuser(request):
    logout(request) 
    request.session.flush() 
    return redirect('loginuser') 


def logoutadmin(request):
    logout(request)
    request.session.flush()
    return redirect('firstpage')




