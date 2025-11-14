from django.contrib.auth import authenticate,login
from django.shortcuts import render,redirect

# Create your views here.
from core.models import User
from seller.models import Seller

def seller_register(request):
    if request.method=='POST':
        seller=User()
        seller.first_name=request.POST.get('first_name')
        seller.last_name=request.POST.get('last_name')
        seller.email=request.POST.get('email')
        seller.phone_number=request.POST.get('phone')
        seller.password=request.POST.get('password')
        confirm_password=request.POST.get('check_password')

        if confirm_password==seller.password:
            seller.set_password(seller.password)
            seller.role = "seller"
            seller.save()
        else:
            print('password not same')
        sell=Seller()
        sell.shop_name=request.POST.get('shop_name')
        sell.location=request.POST.get('location')
        sell.save()
        redirect('/seller_login')
    return render(request,'register.html')


def seller_login(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')

        seller=authenticate(request,username=email,password=password)

        if seller:
            login(request,seller)
            return redirect('/seller_dashboard')
        else:
            print('invalid')

    return render(request,'sellerlogin.html')
