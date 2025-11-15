from django.contrib.auth import authenticate,login
from django.shortcuts import render,redirect

# Create your views here.
from core.models import User
from seller.models import Seller

def seller_register(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            confirm_password = request.POST.get('check_password')  # ✔ matches HTML field
            shop_name = request.POST.get('shop_name')
            location = request.POST.get('location')

            if password != confirm_password:
                print("Passwords do not match")
                return redirect('/seller/register/')

            if Seller.objects.filter(username=username).exists():
                print("Username already taken")
                return redirect('/seller/register/')

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone,
                role='seller'
            )

            Seller.objects.create(
                user=user,
                shop_name=shop_name,
                location=location
            )

            return redirect('/seller/login/')
        return render(request, 'seller/register.html')

def seller_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        seller = authenticate(request,id=id, username=username, password=password)
        print(seller.role)
        if seller and seller.role=='seller':
            login(request, seller)
            return redirect('/seller/seller_dashboard')
        else:
            print("Invalid credentials")
            return render(request, 'seller/login.html', {
                "error": "Invalid email or password"
            })

    return render(request, 'seller/login.html')


def seller_dashboard(request):

    return render(request,'seller/sellerdashboard.html')


def seller_product(request):

    return render(request,'seller/sellerproducts.html')


def seller_editproduct(request):

    return render(request,'seller/sellereditproduct.html')

def add_product(request):

    return render(request,'seller/selleradditem.html')

def order_products(request):
    return render(request,'seller/sellorder.html')