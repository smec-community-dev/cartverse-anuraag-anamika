import json

from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.db.models import Sum,F,Q,Avg,Count
# Create your views here.
from core.models import User
# from seed import subcategories
from django.utils.text import slugify
from django.db.models.functions import TruncMonth
from seller.models import Seller,Product,ProductImage,SubCategory,Category
from user.models import OrderItem,Order,Review,Customer
from decorators.decorators import role_required

def seller_register(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            confirm_password = request.POST.get('check_password')
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

@role_required("seller", login_url="/seller/login")
def seller_dashboard(request):
    seller = Seller.objects.get(user=request.user)
    review=Review.objects.all()
    if seller.user.role != 'seller':
        return redirect('/seller/login')

    products = Product.objects.filter(seller=seller).order_by('-id')[:3]

    order_items = OrderItem.objects.filter(product__seller=seller).select_related('order', 'product')

    total_revenue = order_items.aggregate(
        revenue=Sum(F('quantity') * F('price'))
    )['revenue'] or 0

    category_revenue = (
        order_items
        .values('product__subcategory__category__category_name')
        .annotate(total_revenue=Sum(F('quantity') * F('price')))
        .order_by('-total_revenue')
    )

    cat_labels = [entry['product__subcategory__category__category_name'] for entry in category_revenue]
    cat_values = [float(entry['total_revenue']) for entry in category_revenue]

    store_rating = Review.objects.filter(product__seller=seller).aggregate(
        avg_rating=Avg('rating')
    )['avg_rating'] or 0

    store_rating = round(store_rating, 1)

    return render(request, 'seller/sellerdashboard.html', {
        "seller": seller,
        "products": products,
        "count": products.count(),
        "order_items": order_items,
        "order_count": order_items.count(),
        "revenue": total_revenue,
        "cat_labels": json.dumps(cat_labels),
        "cat_values": json.dumps(cat_values),
        "r_count":review,
        "store_rating":store_rating
    })

@role_required("seller", login_url="/seller/login")
def seller_product(request):
    seller = Seller.objects.get(user=request.user)
    categories = Category.objects.all()

    if seller.user.role != 'seller':
        return redirect('/seller/login')

    products = Product.objects.filter(seller=seller).annotate(
        total_sold=Sum('orderitem__quantity',default=0),
        total_stock=F('stock')-Sum('orderitem__quantity',default=0),
        total_amount=F('price')*F('orderitem__quantity')
    )


    search = request.GET.get('search')
    if search:
        products = products.filter(product_name__icontains=search)

    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(subcategory__category_id=category_id)

    tab = request.GET.get("tab", "all")

    if tab == "active":
        products = products.filter(total_stock__gt=0)
    elif tab == "outofstock":
        products = products.filter(total_stock__lte=0)

    active_count = products.filter(total_stock__gt=0).count()
    outofstock_count = products.filter(total_stock__lte=0).count()

    # Inventory Alerts
    low_stock = products.filter( total_stock__gt=0, stock__lte=10)
    no_stock = products.filter( total_stock=0)

    paginator = Paginator(products, 2)
    page_no = request.GET.get("page")
    page_obj = paginator.get_page(page_no)

    bestseller = products.order_by('-total_sold')[:3]

    return render(request, 'seller/sellerproducts.html', {
        "seller": seller,
        "page_obj": page_obj,
        "count": products.count(),
        "categories": categories,
        "bestseller": bestseller,
        "active_tab":tab,
        "active_count": active_count,
        "outofstock": outofstock_count,
        "low_stock": low_stock,
        "no_stock": no_stock,
    })

@role_required("seller", login_url="/seller/login")
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

@role_required("seller", login_url="/seller/login")
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

@role_required("seller", login_url="/seller/login")
def seller_delete_product(request,id,slug):
    if request.user.role!='seller':
        return redirect("/seller/login")
    seller=Seller.objects.get(user=request.user)
    product = Product.objects.get(id=id, seller=seller)

    ProductImage.objects.filter(product=product).delete()
    product.delete()
    print('product deleted')
    return redirect('/seller/seller_product')

@role_required("seller", login_url="/seller/login")
def order_products(request):

    seller=Seller.objects.get(user=request.user)
    products=Product.objects.filter(seller=seller)
    order_items = OrderItem.objects.filter(product__seller=seller).select_related('order', 'product').order_by('-id')
    search = request.GET.get('search')
    if search:
        order_items = order_items.filter(
            Q(product__product_name__icontains=search) |
            Q(order__id__icontains=search) |
            Q(order__user__username__icontains=search)
        )
    paginator = Paginator(order_items, 2)
    page_no = request.GET.get("page")
    page_obj = paginator.get_page(page_no)
    return render(request,'seller/sellorder.html', {"seller": seller,"order_item":order_items,'page_obj':page_obj})


@role_required("seller", login_url="/seller/login")
def seller_logout(request):
    seller=request.user
    print(seller)
    if seller and seller.role=='seller':
        logout(request)
        return redirect('/seller/login')

    return render(request, 'seller/login.html')

@role_required("seller", login_url="/seller/login")
def single_order_product(request,slug):
    seller = Seller.objects.get(user=request.user)

    # or_slug=Order.objects.get(slug=slug)
    order_items = OrderItem.objects.filter(order__slug=slug,product__seller=seller)
    if not order_items.exists():
        return HttpResponse('not found')
    order = order_items.first().order
    product = order_items.first().product

    return render(request, 'seller/orderproducts.html', {
        "product": product,
        "order":order,
        "order_item": order_items,
    })

@role_required("seller", login_url="/seller/login")
def seller_profile(request):
    seller = Seller.objects.get(user=request.user)
    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.phone_number = request.POST.get("phone")
        user.save()
        seller.shop_name = request.POST.get("shop_name")
        seller.location = request.POST.get("location")
        seller.save()
        print("updated")

        return redirect("/seller/seller_profile/")

    return render(request, "seller/sellersettings.html", {"seller": seller,"user": user})


@role_required("seller", login_url="/seller/login")
def seller_review(request, product_id, slug):
    seller = Seller.objects.get(user=request.user)

    product = get_object_or_404(
        Product, id=product_id, slug=slug, seller=seller
    )

    review_list = Review.objects.filter(product=product).order_by("-review_date")
    average_rating = review_list.aggregate(avg=Avg("rating"))["avg"] or 0

    total_sold = OrderItem.objects.filter(
        product=product,
        status="Processing"
    ).aggregate(total=Sum("quantity"))["total"] or 0

    remaining_stock = product.stock - total_sold

    # -------------------------------
    # 🔥 Calculate Monthly Revenue
    # -------------------------------
    monthly_data = (
        OrderItem.objects.filter(product=product)
        .annotate(month=TruncMonth("order__order_date"))  # <--- CORRECT FIELD
        .values("month")
        .annotate(
            revenue=Sum(F("quantity") * F("price")),
        )
        .order_by("month")
    )

    month_labels = [d["month"].strftime("%b") for d in monthly_data]
    monthly_revenue = [d["revenue"] for d in monthly_data]
    # Total revenue generated by this product
    total_revenue = (
                        OrderItem.objects.filter(product=product)
                        .aggregate(total=Sum(F("quantity") * F("price")))
                    )["total"] or 0

    # Total units sold
    units_sold = (OrderItem.objects.filter(product=product).aggregate(total=Sum("quantity")))["total"] or 0

    # Average selling price (real)
    if units_sold > 0:
        avg_price = total_revenue / units_sold
    else:
        avg_price = 0

    paginator = Paginator(review_list, 5)
    page_num = request.GET.get("page")
    reviews = paginator.get_page(page_num)

    return render(request, "seller/sellerviewreview.html", {
        "product": product,
        "reviews": reviews,
        "seller": seller,
        "reviews_count": review_list.count(),
        "average_rating": round(average_rating, 1),
        "total_sold": total_sold,
        "remaining_stock": remaining_stock,

        # Pass graph data
        "month_labels": month_labels,
        "monthly_revenue": monthly_revenue,
        "total_revenue": total_revenue,
        "units_sold": units_sold,
        "avg_price": round(avg_price, 2),
    })