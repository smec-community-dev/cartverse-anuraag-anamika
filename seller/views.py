from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.shortcuts import render,redirect

# Create your views here.
from core.models import User
# from seed import subcategories
from django.utils.text import slugify
from seller.models import Seller,Product,ProductImage,SubCategory,Category
from user.models import OrderItem


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

            if User.objects.filter(username=username).exists():
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
    seller = Seller.objects.get(user=request.user)
    print(seller.shop_name)
    if seller.user.role=='seller':
        products = Product.objects.filter(seller=seller).order_by('id')[:3]
        product=Product.objects.filter(seller=seller)

    else:
        return redirect('/seller/login')


    return render(request,'seller/sellerdashboard.html',{"seller":seller,"products":products,"count":products.count()})


def seller_product(request):
    seller = Seller.objects.get(user=request.user)
    category=Category.objects.all()
    print(category)
    print(seller.shop_name)
    if seller.user.role == 'seller':
        products = Product.objects.filter(seller=seller)
        search = request.GET.get('search')
        best_selling=Product.objects.filter(seller=seller).order_by('stock')

        if search:
            products = products.filter(product_name__icontains=search)
        category_id = request.GET.get("category")
        if category_id:
            products = products.filter(category_id=category_id)
    else:
        return redirect('/seller/login')
    paginator=Paginator(products,2)
    page_no=request.GET.get("page")
    page_obj=paginator.get_page(page_no)


    return render(request,'seller/sellerproducts.html',{"seller":seller,"products":products,"page_obj":page_obj,"count":products.count(),"categories":category,'bestseller':best_selling})


def seller_editproduct(request,id,slug):
    if request.user.role!='seller':
        return redirect('/seller/login/')
    seller=Seller.objects.get(user=request.user)
    product=Product.objects.get(id=id,seller=seller)
    subcategories=SubCategory.objects.all()
    if request.method=='POST':
        product.product_name = request.POST.get("product_name")
        product.description = request.POST.get("description")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.subcategory_id = request.POST.get("subcategory")
        product.slug = slugify(product.product_name)
        product.save()
        updated_images=request.FILES.getlist('images')

        for img in updated_images:
            ProductImage.objects.create(product=product,seller=seller,product_image=img)
        return redirect('/seller/seller_product/')

    return render(request,'seller/sellereditproduct.html',{"product":product,"subcategory":subcategories})

def add_product(request):

    if request.user.role != "seller":
        return redirect('/seller/login')

    seller = Seller.objects.get(user=request.user)
    subcategories = SubCategory.objects.all()

    if request.method == "POST":

        product_name = request.POST.get("product_name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        subcategory_id = request.POST.get("subcategory")
        main_image = request.FILES.get("main_image")
        additional_images = request.FILES.getlist("additional_images")

        product = Product.objects.create(
            product_name=product_name,
            description=description,
            price=price,
            stock=stock,
            seller=seller,
            subcategory_id=subcategory_id,
            slug=slugify(product_name)
        )
        if main_image:
            ProductImage.objects.create(
                product=product,
                seller=seller,
                product_image=main_image
            )
        for img in additional_images:
            ProductImage.objects.create(
                product=product,
                seller=seller,
                product_image=img
            )

        return redirect("/seller/seller_dashboard")
    return render(request,'seller/selleradditem.html',{"subcategories":subcategories})


def seller_delete_product(request,id,slug):
    if request.user.role!='seller':
        return redirect("/seller/login")
    seller=Seller.objects.get(user=request.user)
    product = Product.objects.get(id=id, seller=seller)

    ProductImage.objects.filter(product=product).delete()
    product.delete()
    print('product deleted')
    return redirect('/seller/seller_product')

def order_products(request):


    seller=Seller.objects.get(user=request.user)
    products=Product.objects.filter(seller=seller)
    order_items = OrderItem.objects.filter(product__seller=seller).select_related('order', 'product')

    paginator = Paginator(products, 2)
    page_no = request.GET.get("page")
    page_obj = paginator.get_page(page_no)
    return render(request,'seller/sellorder.html', {"seller": seller,"order_item":order_items,'page_obj':page_obj})



def seller_logout(request):
    seller=request.user
    print(seller)
    if seller and seller.role=='seller':
        logout(request)
        return redirect('/seller/login')

    return render(request, 'seller/login.html')

