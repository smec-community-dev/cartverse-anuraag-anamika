from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login
from .models import Customer
from core.models import User,Category
from seller.models import Product,ProductImage

def user_register(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            print("Passwords do not match")
            return redirect('/register/')
        user = User.objects.create_user(
            username=request.POST.get('username'),
            email=request.POST.get('email'),
            password=password,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            phone_number=request.POST.get('phone'),
            role='user'
        )
        Customer.objects.create(
            user=user,
            address=request.POST.get('address')
        )
        return redirect('login')
    return render(request, 'user/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and user.role=='user' :
            login(request, user)
            print('login')
            return redirect('home')
        else:
            print("Invalid username or password")

    return render(request, 'user/login.html')

def user_home(request):

   return render(request,'user/user_home.html',)

def list_products(request):
    products = Product.objects.all().prefetch_related('images')
    return render(request,'user/product_list.html',{'products':products})

def single_product(request, slug):
    try:
        product = Product.objects.prefetch_related('images').get(slug=slug)
    except Product.DoesNotExist:
        return render(request, 'user/not_found.html')
    return render(request, 'user/single.html', {'product': product})

