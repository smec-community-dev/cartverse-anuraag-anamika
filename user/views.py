from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login
from .models import Customer
from core.models import User

def user_register(request):
    if request.method=='POST':
        customer=User()
        customer.first_name=request.POST.get('first_name')
        customer.last_name=request.POST.get('last_name')
        customer.email=request.POST.get('email')
        customer.phone_number=request.POST.get('phone')
        customer.password=request.POST.get('password')
        confirm_password=request.POST.get('password')
        if confirm_password==customer.password:
            customer.set_password(customer.password)
            customer.role='seller'
            customer.save()

        else:
            print('password not same')
        customer1=Customer()
        customer1.address=request.POST.get('address')
        customer1.save()
        return redirect('/login/')
    return render(request,'user/register.html')

def user_login(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')

        user=authenticate(request,username=email,password=password)

        if user:
            login(request,user)
            return redirect('/user_dashboard')
        else:
            print('invalid')

    return render(request,'user/login.html')


