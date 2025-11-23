from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login
from django.contrib import messages
from .models import User
from user.models import Order,OrderItem,Address
from seller.models import Product,ProductImage
from decorators.decorators import role_required
from django.db.models import Sum,Q
from django.db.models.functions import TruncMonth
import calendar
from django.core.paginator import Paginator
from django.utils.timezone import now, timedelta
from django.db import models

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

@role_required("admin", login_url="/admin/login")
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



def view_user(request):

    users=User.objects.exclude(role='admin')
    # --- Filters ---
    search = request.GET.get("search")
    role = request.GET.get("role")
    status = request.GET.get("status")
    date_filter = request.GET.get("date")

    # Search filter
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )

    # Role filter
    if role:
        users = users.filter(role=role)

    # Status filter (using is_active)
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

    # ---- Pagination ----
    paginator = Paginator(users, 10)  # 10 users per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    total_users = users.count()
    total_sellers = users.filter(role='seller').count()
    active_users = User.objects.filter(is_active=True).count()
    suspended_users = User.objects.filter(is_active=False).count()

    return render(request,'admin/users_manage.html',{"total_users":total_users,"total_sellers":total_sellers,"users":users,'active_users':active_users,'suspended_users':suspended_users,"search": search,
        "role": role,
        "status": status,
        "date": date_filter,"page_obj":page_obj})

def suspend_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = False
    user.save()
    return redirect("view_user")

def activate_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect("view_user")

def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect("view_user")

def edit_user(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.role = request.POST.get("role")
        user.is_active = True if request.POST.get("is_active") else False
        user.save()
        return redirect("view_user")

    return render(request, "admin/editprofile.html", {"user": user})

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

def view_user_orders(request, user_id):

    user = get_object_or_404(User, id=user_id)

    status_filter = request.GET.get("status")

    orders = Order.objects.filter(user_id=user_id)

    if status_filter:
        orders = orders.filter(orderitem__status__iexact=status_filter)

    orders = orders.distinct()

    # Get all orders of this user
    orders_qs = Order.objects.filter(user_id=user_id).order_by("-order_date")

    # Pagination
    paginator = Paginator(orders_qs, 10)  # 10 orders per page
    page_number = request.GET.get("page")
    orders = paginator.get_page(page_number)

    # Calculate order stats
    total_orders = orders_qs.count()
    total_spent = orders_qs.aggregate(total=models.Sum("total_amount"))["total"] or 0
    avg_order_value = total_spent / total_orders if total_orders > 0 else 0

    # Days since last order
    if orders_qs.exists():
        last_order = orders_qs.first().order_date
        last_order_days = (now().date() - last_order).days
    else:
        last_order_days = "--"

    # Add summary for each order
    for order in orders:
        items = order.orderitem_set.all()
        order.subtotal = sum(item.price for item in items)
        order.tax_amount = 0
        order.shipping_cost = 0

    order_stats = {
        "total_orders": total_orders,
        "total_spent": total_spent,
        "avg_order_value": round(avg_order_value, 2),
        "last_order_days": last_order_days,
        "status_filter": status_filter,
        "orders":orders
    }

    return render(
        request,
        "admin/user_orders.html",
        {
            "user": user,
            "orders": orders,
            "order_stats": order_stats,
        }
    )
def view_seller_products(request, user_id):
    products = Product.objects.filter(seller_id=user_id)
    return render(request, "core/seller_products.html", {"products": products})
