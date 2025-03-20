from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.core.mail import send_mail
from django.conf import settings
import random
from datetime import datetime, timedelta
from .models import *
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required






def gallery(request):
    if request.method == 'POST' and 'image' in request.FILES:
        myimage = request.FILES['image']
        name = request.POST.get("todo")
        price = request.POST.get("date")
        quantity = request.POST.get("quantity")
        model = request.POST.get("model") 
        obj=Gallery(name=name,model=model, quantity=quantity,price=price,feedimage=myimage,user=request.user)
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


def admin_users(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        # Redirect non-admin users or unauthenticated users
        return redirect('loginuser')

    users = User.objects.all()  # Fetch all users
    return render(request, 'admin_users.html', {'users': users})


def firstpage(request): 
    gallery_images = Gallery.objects.all()  
    if request.user.is_authenticated:
        cart_item_count = Cart.objects.filter(user=request.user).count()
        wishlist_item_count = Wishlist.objects.filter(user=request.user).count() 
    else:
        cart_item_count = 0 
        wishlist_item_count = 0
    return render(request, "userindex.html", {
        "gallery_images": gallery_images,
        "cart_item_count": cart_item_count,
        "wishlist_item_count": wishlist_item_count,
        
    })



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


        gallery_item.name= edit1
        gallery_item.model= edit2
        gallery_item.price= edit3

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





def products(request, id):
    gallery_images = Gallery.objects.filter(pk=id)
    if request.user.is_authenticated:
        cart_item_count = Cart.objects.filter(user=request.user).count()
    else:
        cart_item_count = 0 
    
    return render(request, 'products.html', {
        "gallery_images": gallery_images,
        "cart_item_count": cart_item_count
    })



def add_to_cart(request, id):
    if 'username' in request.session:
        try:
            product = Gallery.objects.get(id=id)
        except Gallery.DoesNotExist:
        
            return redirect('product_not_found')  
    
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
        
        )
        if not created:
            if cart_item.product.quantity > cart_item.quantity:
                cart_item.quantity += 1
            else:
                messages.error(request, "out of stock.")
                return redirect('cart_view')
        else:
            cart_item.quantity = 1
            cart_item.save()
            return redirect('cart_view')

@login_required
def increment_cart(request, id):
    cart_item = get_object_or_404(Cart, pk=id, user=request.user)
    if cart_item.product.quantity > cart_item.quantity:
        cart_item.quantity += 1
        cart_item.save()
    else:
        messages.error(request, "Not enough stock available.")

    return redirect('cart_view')


@login_required
def decrement_cart(request, id):
    cart_item = get_object_or_404(Cart, pk=id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_view')

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    cart_item_count = cart_items.count()
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'cart_item_count': cart_item_count})


@login_required
def delete_cart(request, id):
    cart_item = get_object_or_404(Cart, pk=id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart_view')


@login_required
def add_to_wishlist(request, id):
    # Get the product from the Gallery model
    product = get_object_or_404(Gallery, id=id)
    
    # Check if the product is already in the user's wishlist
    if not Wishlist.objects.filter(user=request.user, product=product).exists():
        # Add the product to the wishlist
        wishlist_item = Wishlist(user=request.user, product=product)
        wishlist_item.save()
        messages.success(request, f'{product.name} added to your wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')
    
    return redirect('wishlist_view')

@login_required
def wishlist_view(request):
    # Get all the products in the user's wishlist
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def remove_from_wishlist(request, id):
    # Get the product object
    product = get_object_or_404(Gallery, id=id)
    
    # Find the wishlist entry for the user and the product
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
    
    # If it exists, delete the item
    if wishlist_item.exists():
        wishlist_item.delete()
        messages.success(request, f'{product.name} has been removed from your wishlist.')
    else:
        messages.info(request, f'{product.name} is not in your wishlist.')
    
    # Redirect back to the wishlist view page
    return redirect('wishlist_view')


def search_results(request):
    query = request.GET.get('q')  # Get the search query from the GET parameters
    results = None  # Default to None if there's no query
    
    if query:
        # Filter Gallery by name or model using the query, case insensitive
        results = Gallery.objects.filter(
            name__icontains=query
        ) | Gallery.objects.filter(
            model__icontains=query
        )
    
    return render(request, 'search_results.html', {'results': results, 'query': query})


@login_required
def myprofile(request):
    # If the user submits the form to update profile
    if request.method == "POST":
        new_email = request.POST.get('email')
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confpassword')
        new_address = request.POST.get('address')
        new_place = request.POST.get('place')
        new_phone_number = request.POST.get('phone_number')

        user = request.user

        # Check for changes in user information
        if new_email != user.email:
            if User.objects.filter(email=new_email).exists():
                messages.error(request, "This email is already taken.")
                return redirect('myprofile')
            user.email = new_email

        if new_username != user.username:
            if User.objects.filter(username=new_username).exists():
                messages.error(request, "This username is already taken.")
                return redirect('myprofile')
            user.username = new_username

        if new_password and new_password == confirm_password:
            user.set_password(new_password)
        elif new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('myprofile')

        # Save changes
        user.save()

        # Update or create the user profile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.address = new_address
        user_profile.place = new_place
        user_profile.phone_number = new_phone_number
        user_profile.save()

        # Re-authenticate the user after changing password
        if new_password:
            messages.success(request, "Your profile has been updated. Please log in again.")
            logout(request)
            return redirect('loginuser')

        messages.success(request, "Your profile has been updated.")
        return redirect('myprofile')  # Redirect to the same page to see the changes

    # Display the user's current profile
    user_profile = UserProfile.objects.filter(user=request.user).first()
    return render(request, 'myprofile.html', {'user_profile': user_profile})





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




