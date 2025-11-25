from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import User,Category,SubCategory
from user.models import Order,OrderItem,Address,Review
from seller.models import Product,ProductImage,Seller
from decorators.decorators import role_required
from django.db.models import Sum,Q
from django.db.models.functions import TruncMonth
import calendar
from django.core.paginator import Paginator
from django.utils.timezone import now, timedelta
from django.db import models,transaction
from django.utils.text import slugify
from django.db.models import Avg, Sum, Count,F
from django.contrib.auth import update_session_auth_hash


# Create your views here.

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        print(user)

        if user is not None:
            if hasattr(user, "role") and user.role == "admin":
                print("ADMIN — redirecting now")
                login(request,user)
                return redirect("/core/dashboard/")
            else:
                messages.error(request, "Only admin users can log in here.")
        else:
            messages.error(request, "Invalid username or password.")

        return redirect("/core/login")

    return render(request,'admin/login.html')

@role_required("admin", login_url="/core/login")
def admin_dashboard(request):

    customer=User.objects.filter(role='customer').count()
    order=Order.objects.all().count()
    total_revenue = Order.objects.aggregate(total=Sum("total_amount"))["total"] or 0

    top_products = (
        Product.objects
        .filter(orderitem__isnull=False)
        .annotate(total_sold=Sum("orderitem__quantity"))
        .order_by("-total_sold")[:4]
    )

    if customer > 0:
        conversion_rate = (order/ customer) * 100
    else:
        conversion_rate = 0


    # ******************************
    # 📊 Monthly Revenue Aggregation
    # ******************************
    monthly_revenue = (
        Order.objects.annotate(month=TruncMonth("order_date"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )

    labels = []
    data = []

    for entry in monthly_revenue:
        month_number = entry["month"].month
        month_name = calendar.month_abbr[month_number]  # Jan, Feb, ...
        labels.append(month_name)
        data.append(float(entry["total"]))

    recent_orders = Order.objects.select_related("user").order_by("-order_date")[:5]


    return render(request,'admin/admindashboard.html',{"customer":customer,"order_count":order,"total_revenue": total_revenue,"conversion_rate": round(conversion_rate, 2),"chart_labels": labels,"chart_data": data,"top_products":top_products,"recent_orders":recent_orders})


@role_required("admin", login_url="/core/login")
def view_user(request):
    users = User.objects.exclude(role='admin')

    search = request.GET.get("search") or ""
    role = request.GET.get("role") or ""
    status = request.GET.get("status") or ""
    date_filter = request.GET.get("date") or ""

    # Search filter
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )

    # Role filter
    if role:
        users = users.filter(role=role)

    # Status filter
    if status == "active":
        users = users.filter(is_active=True)
    elif status == "suspended":
        users = users.filter(is_active=False)

    # Date filter
    if date_filter == "7":
        users = users.filter(date_joined__gte=now() - timedelta(days=7))
    elif date_filter == "30":
        users = users.filter(date_joined__gte=now() - timedelta(days=30))
    elif date_filter == "365":
        users = users.filter(date_joined__gte=now() - timedelta(days=365))

    # Pagination
    paginator = Paginator(users, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    total_users = users.count()
    total_sellers = users.filter(role='seller').count()
    active_users = User.objects.filter(is_active=True).count()
    suspended_users = User.objects.filter(is_active=False).count()

    return render(request, 'admin/users_manage.html', {
        "users": page_obj,        # <---- FIXED
        "page_obj": page_obj,
        "total_users": total_users,
        "total_sellers": total_sellers,
        "active_users": active_users,
        "suspended_users": suspended_users,
        "search": search,
        "role": role,
        "status": status,
        "date": date_filter,
    })

@role_required("admin", login_url="/core/login")
def suspend_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = False
    user.save()
    return redirect("/core/users")


@role_required("admin", login_url="/core/login")
def activate_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect("/core/users")


@role_required("admin", login_url="/core/login")
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect("/core/users")



@role_required("admin", login_url="/core/login")
def edit_user(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.role = request.POST.get("role")
        user.is_active = True if request.POST.get("is_active") else False
        user.save()
        return redirect("/core/users")

    return render(request, "admin/editprofile.html", {"user": user})


@role_required("admin", login_url="/core/login")
def view_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Fetch user orders
    orders = Order.objects.filter(user=user)

    # Stats
    total_orders = orders.count()
    total_spent = orders.aggregate(total=Sum("total_amount"))["total"] or 0
    joined_days = (now().date() - user.date_joined.date()).days
    rating = 4.6  # default or calculate from seller reviews

    user_stats = {
        "orders": total_orders,
        "total_spent": total_spent,
        "joined_days": joined_days,
        "rating": rating,
    }

    # Addresses (if using custom address model)
    addresses = Address.objects.filter(user=user)



    return render(request, "admin/view_profile.html", {
        "user": user,
        "user_stats": user_stats,
        "addresses": addresses,
    })


@role_required("admin", login_url="/core/login")
def view_user_orders(request, user_id):

    user = get_object_or_404(User, id=user_id)

    status_filter = request.GET.get("status", "")
    search_query = request.GET.get("search", "")

    # BASE QuerySet
    orders_qs = Order.objects.filter(user_id=user_id).order_by("-order_date")
    # Apply Search
    if search_query:
        orders_qs = orders_qs.filter(
            Q(id__icontains=search_query) |
            Q(slug__icontains=search_query) |
            Q(orderitem__product__product_name__icontains=search_query) |
            Q(orderitem__product__slug__icontains=search_query)
        ).distinct()

    # Apply Status Filter
    if status_filter:
        orders_qs = orders_qs.filter(orderitem__status__iexact=status_filter).distinct()

    # ---- Pagination ----
    paginator = Paginator(orders_qs, 10)
    page_number = request.GET.get("page")
    orders = paginator.get_page(page_number)

    # Order Stats
    total_orders = orders_qs.count()
    total_spent = orders_qs.aggregate(total=models.Sum("total_amount"))["total"] or 0
    avg_order_value = round(total_spent / total_orders, 2) if total_orders > 0 else 0

    # Days since last order
    if orders_qs.exists():
        last_order_date = orders_qs.first().order_date
        last_order_days = (now().date() - last_order_date).days
    else:
        last_order_days = "--"

    order_stats = {
        "total_orders": total_orders,
        "total_spent": total_spent,
        "avg_order_value": avg_order_value,
        "last_order_days": last_order_days,
        "status_filter": status_filter,
        "search": search_query,
    }

    # Add extra fields for each order
    for order in orders:
        items = order.orderitem_set.all()
        order.subtotal = sum(item.price for item in items)
        order.tax_amount = 0
        order.shipping_cost = 0

    return render(
        request,
        "admin/user_orders.html",
        {
            "user": user,
            "orders": orders,               # paginated order list
            "order_stats": order_stats,
            "status_filter": status_filter,
            "search": search_query,
        }
    )



@role_required("admin", login_url="/core/login")
def view_seller_products(request, user_id):

    seller = get_object_or_404(Seller, user_id=user_id)

    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")
    category_filter = request.GET.get("category", "")

    products = (
        Product.objects.filter(seller=seller)
        .prefetch_related("images", "subcategory__category")
        .annotate(
            total_sold=Sum("orderitem__quantity"),
            revenue=Sum("orderitem__price"),
            review_count=Count("review"),
            avg_rating=Avg("review__rating"),
        )
    )

    # SEARCH
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(id__icontains=search_query)
        )

    # STATUS FILTER
    if status_filter == "active":
        products = products.filter(stock__gt=10)
    elif status_filter == "lowstock":
        products = products.filter(stock__gt=0, stock__lte=10)
    elif status_filter == "outofstock":
        products = products.filter(stock=0)

    # CATEGORY FILTER
    if category_filter:
        products = products.filter(subcategory__category__category_name=category_filter)

    # PAGINATION
    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    products_page = paginator.get_page(page_number)

    # SUMMARY STATS
    product_stats = {
        "total_products": products.count(),
        "active_products": products.filter(stock__gt=0).count(),
        "low_stock": products.filter(stock__lte=10, stock__gt=0).count(),
        "out_of_stock": products.filter(stock=0).count(),
    }

    return render(request, "admin/seller_products.html", {
        "seller": seller,
        "products": products_page,        # <-- FIXED
        "product_stats": product_stats,   # <-- FIXED
        "search_query": search_query,
        "status_filter": status_filter,
        "category_filter": category_filter,
    })
@role_required("admin", login_url="/core/login")
def add_user(request):
    if request.method == "POST":

        # BASIC USER FIELDS
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")
        first_name = request.POST.get("firstName")
        last_name = request.POST.get("lastName")
        phone_number = request.POST.get("phone")
        role = request.POST.get("role")
        is_active = request.POST.get("is_active") == "on"

        # SELLER FIELDS
        shop_name = request.POST.get("shop_name")
        shop_description = request.POST.get("shop_description")

        # ---------------- VALIDATION ----------------
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("add_user")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("add_user")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("add_user")

        # ---------------- CREATE USER ----------------
        try:
            with transaction.atomic():
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    role=role,
                    is_active=is_active,
                    password=make_password(password),
                )

                # If seller → create seller profile
                if role == "seller":
                    Seller.objects.create(
                        user=user,
                        shop_name=shop_name,
                        location=shop_description or "",
                    )

        except Exception as e:
            messages.error(request, f"Error creating user: {e}")
            return redirect("add_user")

        messages.success(request, "User created successfully!")
        return redirect("users_list")  # Change if needed

    return render(request, "admin/add_user.html")

@role_required("admin", login_url="/core/login")
def admin_products(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    seller = request.GET.get('seller', '')

    products = Product.objects.all()

    if search:
        products = products.filter(
            Q(product_name__icontains=search) |
            Q(slug__icontains=search)
        )

    if status:
        if status == "active":
            products = products.filter(stock__gt=10)
        elif status == "lowstock":
            products = products.filter(stock__lte=10, stock__gt=0)
        elif status == "outofstock":
            products = products.filter(stock=0)

    if category:
        products = products.filter(subcategory__category_id=category)

    if seller:
        products = products.filter(seller_id=seller)


    # --- STATISTICS ---
    total_products = Product.objects.count()
    active_products = Product.objects.filter(stock__gt=10).count()
    low_stock = Product.objects.filter(stock__gt=0, stock__lte=10).count()
    out_of_stock = Product.objects.filter(stock=0).count()


    # Pagination
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'admin/view_products.html', {
        'products': page_obj,
        'page_obj': page_obj,

        'search': search,
        'status': status,
        'category': category,
        'seller': seller,
        'categories': Category.objects.all(),
        'sellers': Seller.objects.all(),
        "total_products": total_products,
        "active_products": active_products,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock
    })



@role_required("admin", login_url="/core/login")
def product_detail_view(request, id):
    # Fetch product using ID
    product = get_object_or_404(Product, id=id)

    # Fetch associated images
    images = ProductImage.objects.filter(product=product)

    # Prepare main image (first image)
    main_image = images.first() if images.exists() else None
    reviews = Review.objects.filter(product=product).select_related("user")

    context = {
        "product": product,
        "images": images,
        "main_image": main_image,
        "seller": product.seller,
        "subcategory": product.subcategory,
        "category": product.subcategory.category if hasattr(product.subcategory, "category") else None,
        "reviews": reviews,
    }

    return render(request, "admin/singleproduct.html", context)




@role_required("admin", login_url="/core/login")
def delete_product_view(request, id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=id)

        # Delete related images
        ProductImage.objects.filter(product=product).delete()

        product_name = product.product_name
        product.delete()

        messages.success(request, f"Product '{product_name}' has been deleted.")
        return redirect("/admin/products/")   # redirect to product list

    return redirect("/admin/products/")




@role_required("admin", login_url="/core/login")
def admin_seller_profile(request, id):
    seller = get_object_or_404(Seller, id=id)

    # Recent products (limit 3)
    recent_products = Product.objects.filter(seller=seller).order_by("-id")[:3]

    # Total products
    total_products = Product.objects.filter(seller=seller).count()

    # Total sales = number of sold items
    total_sales = OrderItem.objects.filter(product__seller=seller).count()

    # Total revenue
    total_revenue = OrderItem.objects.filter(product__seller=seller).aggregate(
        total=Sum("price")
    )["total"] or 0

    # Average rating
    avg_rating = Review.objects.filter(product__seller=seller).aggregate(
        rating=Avg("rating")
    )["rating"] or 0

    context = {
        "seller": seller,
        "recent_products": recent_products,
        "total_products": total_products,
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "avg_rating": round(avg_rating, 1),
    }

    return render(request, "admin/product_sellerinfo.html", context)



@role_required("admin", login_url="/core/login")
def admin_products_by_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    products = Product.objects.filter(seller=seller)

    return render(request, "admin/seller_products.html", {
        "seller": seller,
        "products": products
    })


from django.contrib import messages


@role_required("admin", login_url="/core/login")
def admin_send_warning(request, id):
    seller = get_object_or_404(Seller, id=id)

    # You can implement notifications/email later
    messages.success(request, f"Warning sent to {seller.shop_name}.")

    return redirect("admin-seller-profile", id=id)


@role_required("admin", login_url="/core/login")
def admin_suspend_seller(request, id):
    seller = get_object_or_404(Seller, id=id)

    # Suspend the user account
    seller.user.is_active = False
    seller.user.save()

    messages.error(request, f"{seller.shop_name}'s account has been suspended.")

    return redirect("admin-seller-profile", id=id)


from django.core.paginator import Paginator
from django.db.models import Q, Count



@role_required("admin", login_url="/core/login")
def admin_orders_view(request):

    # -------------------------------
    # 1️⃣ SEARCH
    # -------------------------------
    search_query = request.GET.get("search", "")

    orders = Order.objects.all().order_by("-id")  # newest first

    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(orderitem__product__product_name__icontains=search_query)
        ).distinct()

    # -------------------------------
    # 2️⃣ STATUS FILTER (orderitem-based)
    # -------------------------------
    status_filter = request.GET.get("status", "")

    if status_filter:
        orders = orders.filter(orderitem__status=status_filter).distinct()

    # -------------------------------
    # 3️⃣ PAGINATION
    # -------------------------------
    paginator = Paginator(orders, 10)  # 10 orders per page
    page_number = request.GET.get("page")
    orders_page = paginator.get_page(page_number)

    # -------------------------------
    # 4️⃣ STATISTICS (based on OrderItem)
    # -------------------------------
    total_orders = Order.objects.count()
    completed = OrderItem.objects.filter(status="Delivered").count()
    pending = OrderItem.objects.filter(status="Pending").count()
    cancelled = OrderItem.objects.filter(status="Cancelled").count()

    context = {
        "orders": orders_page,
        "total_orders": total_orders,
        "completed": completed,
        "pending": pending,
        "cancelled": cancelled,
        "search_query": search_query,
        "status_filter": status_filter
    }

    return render(request, "admin/orders_page.html", context)


@role_required("admin", login_url="/core/login")
def admin_order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # --------------------------
    # ORDER ITEMS
    # --------------------------
    items = OrderItem.objects.filter(order=order)

    # Total items
    total_items = items.aggregate(total=Sum("quantity"))["total"] or 0

    # Calculate subtotal (NOT saved in DB)
    subtotal = items.aggregate(
        total=Sum(F("price") * F("quantity"))
    )["total"] or 0

    # --------------------------
    # ORDER STATUS derived from items (no order.status)
    # --------------------------
    if items.exists():
        statuses = list(items.values_list("status", flat=True).distinct())

        if "Pending" in statuses:
            order_status = "Pending"
        elif "Cancelled" in statuses:
            order_status = "Cancelled"
        elif "Shipped" in statuses and "Delivered" in statuses:
            order_status = "Shipped"
        elif "Shipped" in statuses:
            order_status = "Shipped"
        elif statuses == ["Delivered"] or statuses == list(set(["Delivered"])):
            order_status = "Delivered"
        else:
            order_status = statuses[0]
    else:
        order_status = "Pending"

    # --------------------------
    # STATUS UPDATE
    # --------------------------
    if request.method == "POST":
        new_status = request.POST.get("status")
        notes = request.POST.get("notes")

        if new_status:
            items.update(status=new_status)
            messages.success(request, f"Order status updated to {new_status}.")
            return redirect("admin-order-detail", order_id=order.id)

    # --------------------------
    # TIMELINE
    # --------------------------
    timeline = {
        "placed": True,
        "payment": order_status != "Pending",
        "processing": order_status in ["Processing", "Shipped", "Delivered"],
        "shipped": order_status in ["Shipped", "Delivered"],
        "delivered": order_status == "Delivered",
    }

    context = {
        "order": order,
        "items": items,
        "total_items": total_items,

        # THIS is what your HTML should use
        "order_total": subtotal,
        "subtotal": subtotal,

        "order_status": order_status,
        "timeline": timeline,
    }

    return render(request, "admin/order_detail.html", context)

@role_required("admin", login_url="/core/login")
def admin_order_delete_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        order.delete()
        messages.success(request, "Order deleted successfully!")
        return redirect("admin-orders")

    # Optional: confirmation page
    return render(request, "admin/order_delete_confirm.html", {"order": order})


@role_required("admin", login_url="/core/login")
def admin_sellers_view(request):

    # --------------------------------
    # 1️⃣ SEARCH (username, email, shop name)
    # --------------------------------
    search_query = request.GET.get("search", "")

    sellers = Seller.objects.all().select_related("user").annotate(
        product_count=Count("product", distinct=True),
        order_count=Count("product__orderitem", distinct=True),
        total_revenue=Sum(F("product__orderitem__quantity") * F("product__orderitem__price"), distinct=True),
        avg_rating=Avg("product__review__rating")
    )

    if search_query:
        sellers = sellers.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(shop_name__icontains=search_query)
        )

    # --------------------------------
    # 2️⃣ FILTER BY STATUS (active / inactive)
    # --------------------------------
    status_filter = request.GET.get("status", "")
    if status_filter == "active":
        sellers = sellers.filter(user__is_active=True)
    elif status_filter == "inactive":
        sellers = sellers.filter(user__is_active=False)

    # --------------------------------
    # 3️⃣ PAGINATION
    # --------------------------------
    paginator = Paginator(sellers, 10)   # 10 sellers per page
    page_no = request.GET.get("page")
    sellers_page = paginator.get_page(page_no)

    # --------------------------------
    # 4️⃣ GLOBAL STATISTICS
    # --------------------------------
    total_sellers = Seller.objects.count()
    active_sellers = Seller.objects.filter(user__is_active=True).count()
    inactive_sellers = Seller.objects.filter(user__is_active=False).count()
    total_revenue = (
            OrderItem.objects.aggregate(
                total=Sum(F("quantity") * F("price"))
            )["total"] or 0
    )

    context = {
        "sellers": sellers_page,
        "total_sellers": total_sellers,
        "active_sellers": active_sellers,
        "inactive_sellers": inactive_sellers,
        "search_query": search_query,
        "status_filter": status_filter,
        "total_revenue": total_revenue,
    }

    return render(request, "admin/seller_page.html", context)


@role_required("admin", login_url="/core/login")
def admin_seller_detail(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)

    # Get products
    products = Product.objects.filter(seller=seller)
    total_products = products.count()

    # Get order items
    order_items = OrderItem.objects.filter(product__seller=seller)

    # Total orders (order items count)
    total_orders = order_items.count()

    # Total revenue
    total_revenue = (
        order_items.aggregate(
            total=Sum(F("quantity") * F("price"))
        )["total"] or 0
    )

    # Average rating
    avg_rating = (
        Review.objects.filter(product__seller=seller)
        .aggregate(avg=Avg("rating"))["avg"] or 0
    )
    avg_rating = round(avg_rating, 1)

    # All product data (for table)
    product_data = []
    for product in products:
        order_count = OrderItem.objects.filter(product=product).aggregate(
            total=Sum("quantity")
        )["total"] or 0

        rating = (
            Review.objects.filter(product=product).aggregate(avg=Avg("rating"))["avg"] or 0
        )

        product_data.append({
            "product": product,
            "order_count": order_count,
            "avg_rating": round(rating, 1),
        })

    context = {
        "seller": seller,
        "products": product_data,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "avg_rating": avg_rating,
    }

    return render(request, "admin/seller_detail.html", context)



@role_required("admin", login_url="/core/login")
def admin_seller_delete(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)

    # Delete user + seller profile
    user = seller.user

    seller.delete()
    user.delete()

    messages.success(request, "Seller deleted successfully.")
    return redirect("/admin/sellers/")

@role_required("admin", login_url="/core/login")
def admin_category_view(request):
    search = request.GET.get("search", "")

    categories = Category.objects.annotate(
        product_count=Count("subcategory__product", distinct=True)
    )

    # search
    if search:
        categories = categories.filter(category_name__icontains=search)

    # pagination
    paginator = Paginator(categories, 10)
    page_number = request.GET.get("page")
    categories_page = paginator.get_page(page_number)

    context = {
        "categories": categories_page,
        "search": search,
        "total_categories": Category.objects.count(),
    }
    return render(request, "admin/category.html", context)


@role_required("admin", login_url="/core/login")
def view_categories(request):
    search = request.GET.get("search", "")

    # Annotate product count for each category
    categories = Category.objects.annotate(
        product_count=Count("subcategory__product")
    )

    # SEARCH
    if search:
        categories = categories.filter(
            Q(category_name__icontains=search)
        )

    # PAGINATION
    paginator = Paginator(categories, 10)  # Show 10 per page
    page_number = request.GET.get("page")
    categories_page = paginator.get_page(page_number)

    # Stats
    total_categories = Category.objects.count()
    total_products = Product.objects.count()

    context = {
        "categories": categories_page,
        "total_categories": total_categories,
        "total_products": total_products,
        "search": search,
    }

    return render(request, "admin/category.html", context)


@role_required("admin", login_url="/core/login")
def view_subcategories(request):
    search_query = request.GET.get("search", "")
    category_filter = request.GET.get("category", "")

    # Count products under each subcategory
    subcategories = SubCategory.objects.annotate(product_count=Count("product"))

    # ─── SEARCH FILTER ───────────────────────────────
    if search_query:
        subcategories = subcategories.filter(
            Q(sub_category_name__icontains=search_query) |
            Q(category__category_name__icontains=search_query)
        )

    # ─── CATEGORY FILTER ─────────────────────────────
    if category_filter:
        subcategories = subcategories.filter(category_id=category_filter)

    # ─── PAGINATION ──────────────────────────────────
    paginator = Paginator(subcategories, 10)
    page_number = request.GET.get("page")
    subcategories_page = paginator.get_page(page_number)

    # ─── STATS FOR CARDS ─────────────────────────────
    total_subcategories = SubCategory.objects.count()
    total_products = Product.objects.count()

    categories = Category.objects.all()

    context = {
        "subcategories": subcategories_page,
        "categories": categories,
        "search_query": search_query,
        "category_filter": category_filter,

        # stats
        "total_subcategories": total_subcategories,
        "total_products": total_products,
    }


    return render(request, "admin/subcategory.html", context)


@role_required("admin", login_url="/core/login")
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("category_name")
        image = request.FILES.get("image")  # ← file upload

        Category.objects.create(
            category_name=name,
            slug=slugify(name),
            image=image
        )

        return redirect("admin-categories")

    return render(request, "admin/addcategory.html")

@role_required("admin", login_url="/core/login")
def add_subcategory(request):
    categories = Category.objects.all()

    if request.method == "POST":
        category_id = request.POST.get("category")
        sub_name = request.POST.get("sub_category_name")

        category = get_object_or_404(Category, id=category_id)

        SubCategory.objects.create(
            category=category,
            sub_category_name=sub_name,
            slug=slugify(sub_name)
        )

        return redirect("admin-subcategories")  # or your subcategory list

    return render(request, "admin/addsubcategory.html", {
        "categories": categories
    })


@role_required("admin", login_url="/core/login")
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect("admin-categories")


@role_required("admin", login_url="/core/login")
def delete_subcategory(request, id):
    sub = get_object_or_404(SubCategory, id=id)
    sub.delete()
    return redirect("admin-subcategories")


@role_required("admin", login_url="/core/login")
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        name = request.POST.get("category_name")
        image = request.FILES.get("image")  # optional

        category.category_name = name
        category.slug = slugify(name)

        if image:
            category.image = image  # update only if new image uploaded

        category.save()
        return redirect("admin-categories")

    return render(request, "admin/editcategory.html", {"category": category})


@role_required("admin", login_url="/core/login")
def edit_subcategory(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    categories = Category.objects.all()

    if request.method == "POST":
        sub_name = request.POST.get("name")  # <-- Correct field name
        category_id = request.POST.get("category")

        # Validation
        if not sub_name:
            messages.error(request, "Subcategory name cannot be empty.")
            return redirect("edit-subcategory", pk=pk)

        subcategory.sub_category_name = sub_name
        subcategory.category_id = category_id
        subcategory.slug = slugify(sub_name)

        subcategory.save()
        return redirect("/core/subcategories")

    return render(request, "admin/editsubcategory.html", {
        "subcategory": subcategory,
        "categories": categories
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@role_required("admin", login_url="/core/login")
def admin_profile(request):
    admin_user = request.user   # Logged-in admin

    context = {
        "admin": admin_user,
    }

    return render(request, "admin/admin_profile.html", context)

@role_required("admin", login_url="/core/login")
def update_profile(request):
    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")

        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("admin-profile")

    return redirect("admin-profile")

@role_required("admin", login_url="/core/login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect!")
            return redirect("admin-profile")

        request.user.set_password(new_password)
        request.user.save()

        update_session_auth_hash(request, request.user)

        messages.success(request, "Password changed successfully!")
        return redirect("admin-profile")

    return redirect("admin-profile")
