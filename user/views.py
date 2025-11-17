from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login
from .models import Customer
from core.models import User,Category
from seller.models import Product,ProductImage
from django.contrib import messages
from user.decorators import customer_required
from django.core.paginator import Paginator

def user_register(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')

        if password!=confirm_password:
            print('password is incorrect')
            messages.error(request,'password is incorrect')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request,'email already exist')
            return redirect('register')

        user=User.objects.create_user(
            username=request.POST.get('username'),
            email=email,
            password=password,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            phone_number=request.POST.get('phone'),
            role='customer'
        )

        Customer.objects.create(
            user=user,
            address=request.POST.get('address'),
        )
        return redirect('login')
    return render(request,'user/register.html')

def user_login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user=authenticate(request,username=username,password=password)

        if user and user.role=="customer":
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'invalid username or password')

    return render(request,'user/login.html')




def product_list(request):
        products=Product.objects.prefetch_related('images').all()
        paginator = Paginator(products, 6)  # 6 products per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'user/user_home.html',{"page_obj":page_obj})

def single_products(request,slug):
    product = Product.objects.prefetch_related('images').get(slug=slug)
    all_images = product.images.all()
    return render(request, 'user/single.html', { 'product': product, 'all_images': all_images })
