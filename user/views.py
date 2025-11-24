from re import search

from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.utils.text import normalize_newlines
from django.shortcuts import get_object_or_404
from decorators.decorators import role_required
from .models import Customer, Wishlist,Cart,Order,OrderItem,Address,Review,ReviewImage
from core.models import User,Category,SubCategory
from seller.models import Product,ProductImage
from django.contrib import messages
from django.core.paginator import Paginator
from decorators.decorators import role_required
from django.db.models import Q
import razorpay
from django.conf import settings

razorpay_client = razorpay.Client(auth=(
    settings.RAZORPAY_KEY_ID,
    settings.RAZORPAY_KEY_SECRET
))


#for user registration
def user_register(request):
    request.session['role'] = 'user'
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')

        if password!=confirm_password:
            print('password is incorrect')
            messages.error(request,'password is incorrect')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another one.")
            return redirect("register")

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

#for user login
def user_login(request):
    request.session['role'] = 'user'
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


#home page functions
def home(request):
    category = Category.objects.all()
    products = Product.objects.all()[:4]

    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart_count = Cart.objects.filter(user=request.user).count()
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    else:
        wishlist_count = 0
        cart_count = 0
        wishlist_ids = []

    return render(request, 'user/home.html', {
        'category': category,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
        'product': products,
        'wishlist_ids': wishlist_ids,
    })

#for expolre products
def explore_products(request, slug):

    try:
        category = Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        return redirect("user_home")

    subcategories = SubCategory.objects.filter(category=category)

    selected_sub = request.GET.get("subcategory")

    if selected_sub:
        products = Product.objects.filter(subcategory__slug=selected_sub).prefetch_related("images")
    else:
        products = Product.objects.filter(subcategory__in=subcategories).prefetch_related("images")

    return render(request, "user/explore.html", {
        "category": category,
        "products": products,
        "subcategories": subcategories,
        "selected_sub": selected_sub,
        "products_count": products.count(),
    })



#for subcategories and category html page
def subcategory(request, slug=None):
    subcategories = SubCategory.objects.all()
    products = Product.objects.all()
    search_query = request.GET.get('search', '').strip()
    selected_sub = None
    if slug:
        selected_sub = get_object_or_404(SubCategory, slug=slug)
        products = products.filter(subcategory=selected_sub)

    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(subcategory__sub_category_name__icontains=search_query) |
            Q(subcategory__category__category_name__icontains=search_query)
        )

    paginator = Paginator(products, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request, 'user/category.html', {

        'subcategories': subcategories,
        'products': page_obj,
        'selected_sub': selected_sub,
        'search_query': search_query

    })


#for about
def about(request):
    return render(request,'user/about.html')

#for home page
def user_home(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # GET parameters
    search = request.GET.get('search', '')
    selected_category = request.GET.get('category', '')
    selected_subcategory = request.GET.get('subcategory', '')
    sort_price = request.GET.get('sort_price', '')
    instock = request.GET.get('instock')
    onsale = request.GET.get('onsale')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Filter by category
    if selected_category:
        products = products.filter(subcategory__category__slug=selected_category)

    # Filter by subcategory
    if selected_subcategory:
        products = products.filter(subcategory__slug=selected_subcategory)

    # Search filter (product name, subcategory name, or category name)
    if search:
        products = products.filter(
            Q(product_name__icontains=search) |
            Q(subcategory__sub_category_name__icontains=search) |
            Q(subcategory__category__category_name__icontains=search)
        )

    # Stock filter
    if instock:
        products = products.filter(stock__gt=0)

    # On sale filter
    if onsale:
        products = products.filter(discount_price__isnull=False)

    # Price filter
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sorting
    if sort_price == 'low':
        products = products.order_by('price')
    elif sort_price == 'high':
        products = products.order_by('-price')
    elif sort_price == 'newest':
        products = products.order_by('-id')
    elif sort_price == 'popular':
        products = products.order_by('-stock')


    paginator = Paginator(products, 4)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'products': products,
        'categories': categories,
        'search': search,
        'selected_category': selected_category,
        'selected_subcategory': selected_subcategory,
        'sort_price': sort_price,
        'instock': instock,
        'onsale': onsale,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'user/user_home.html', context)
def single_products(request, slug):
    product = Product.objects.prefetch_related('images').get(slug=slug)

    # Get all reviews for this product + their images
    reviews = (
        Review.objects
        .filter(product=product)
        .select_related('user')
        .prefetch_related('images')   # <-- FIXED HERE
    )

    all_images = product.images.all()

    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart_count = Cart.objects.filter(user=request.user).count()
    else:
        wishlist_count = 0
        cart_count = 0

    return render(request, 'user/single.html', {
        'product': product,
        'image': all_images,
        'reviews': reviews,
        'count': wishlist_count,
        'cart': cart_count,
    })


@role_required('customer','/user/login')
def add_wishlist(request,slug):
    product=Product.objects.get(slug=slug)

    if Wishlist.objects.filter(user=request.user,product=product).exists():
        messages.error(request, "Product already in your wishlist.")
        return redirect('single',slug=product.slug)

    Wishlist.objects.create(user=request.user, product=product)
    messages.success(request, "Added to wishlist!")
    return redirect("single", slug=product.slug)


@role_required('customer','/user/login')
def view_wishlist(request):
    wishlist=Wishlist.objects.filter(user=request.user).select_related("product").prefetch_related('product__images')
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart_count = Cart.objects.filter(user=request.user).count()
    else:
        wishlist_count = 0
        cart_count = 0
    return render(request,'user/wishlist.html',{'x':wishlist,'count':wishlist_count,'cart':cart_count})

@role_required('customer','/user/login')
def remove_wishlist(request,slug):
    product=Product.objects.get(slug=slug)

    wishlist_item=Wishlist.objects.filter(user=request.user,product=product).first()
    if wishlist_item:
        wishlist_item.delete()
        messages.success(request,'wishlist item removed succesfully!')
    else:
        messages.error(request,'wishlist item not removed')
    return redirect('wishlist')




@role_required('customer','/user/login')
def user_logout(request):
    user=request.user
    if user and user.role=='customer':
        logout(request)
        return redirect('home')
    return render(request,'user/login.html')

@role_required('customer', '/user/login')
def add_cart(request, slug):
        product = Product.objects.get(slug=slug)
        qty = int(request.POST.get("quantity", 1))

        # Prevent adding more than stock
        if qty > product.stock:
            messages.error(request, "Only limited stock available.")
            return redirect("single", slug=slug)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={"price": product.price, "quantity": qty}
        )

        if not created:
            if cart_item.quantity + qty <= product.stock:
                cart_item.quantity += qty
                cart_item.save()
                messages.success(request, "Quantity updated in cart.")
            else:
                messages.error(request, "Stock limit reached.")
                return redirect("single", slug=slug)
        else:
            messages.success(request, "Product added to cart.")

        return redirect("cart")


@role_required('customer','/user/login')
def remove_cart(request, cart_id):
    cart_item = Cart.objects.get( id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart")

@role_required('customer', '/user/login')
def update_quantity(request, cart_id):
    if request.method == "POST":
        cart_item = Cart.objects.get(id=cart_id, user=request.user)
        try:
            qty = int(request.POST.get("quantity", 1))
        except ValueError:
            messages.error(request, "Invalid quantity.")
            return redirect("cart")

        if qty < 1:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
        elif qty > cart_item.product.stock:
            messages.error(request, f"Only {cart_item.product.stock} items available.")
        else:
            cart_item.quantity = qty
            cart_item.save()
            messages.success(request, "Cart updated successfully.")

    return redirect("cart")


def cart(request):
    print("=== DEBUG GOOGLE LOGIN ===")
    print("User:", request.user)
    print("Authenticated:", request.user.is_authenticated)
    print("Role:", getattr(request.user, "role", None))
    print("Customer exists:", Customer.objects.filter(user=request.user).exists())
    print("==========================")
    print("User:", request.user)
    print("Authenticated:", request.user.is_authenticated)
    cart_items = Cart.objects.filter(user=request.user)

    total = sum(item.price * item.quantity for item in cart_items)

    return render(request, "user/cart.html", {"cart_items": cart_items, "total": total})




@role_required('customer', '/user/login')
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("review_comment")
        images = request.FILES.getlist('review_images')  # multiple images

        # Validate rating
        if not rating or int(rating) < 1 or int(rating) > 5:
            messages.error(request, "Rating must be between 1 and 5.")
            return redirect("single", slug=product.slug)

        rating = int(rating)

        # Check if user already reviewed
        review, created = Review.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={"rating": rating, "review_comment": comment}
        )

        # If review exists → update it
        if not created:
            review.rating = rating
            review.review_comment = comment
            review.save()

            # Delete old images if updating
            ReviewImage.objects.filter(review=review).delete()

        # Save images
        for img in images:
            ReviewImage.objects.create(review=review, image=img)

        messages.success(request, "Your review has been submitted!")
        return redirect("single", slug=product.slug)

    return render(request, "user/review.html", {
        "product": product
    })

@role_required('customer', '/user/login')
def add_address(request):
    user_addresses = Address.objects.filter(user=request.user)
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        address_line1 = request.POST.get("address_line1")
        address_line2 = request.POST.get("address_line2")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")
        country = request.POST.get("country", "India")
        is_default = request.POST.get("is_default") == "on"

        if not (full_name and phone and address_line1 and city and state and pincode):
            messages.error(request, "Please fill in all required fields.")
            return redirect("add_address")


        Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            pincode=pincode,
            country=country,
            is_default=is_default,
        )

        messages.success(request, "Address added successfully!")
      # redirect wherever needed
        return redirect('profile')
    return render(request, "user/address.html",{"user_addresses": user_addresses})



@role_required('customer', '/user/login')
def edit_address(request, address_id):

    address = Address.objects.get( id=address_id, user=request.user)

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        address_line1 = request.POST.get("address_line1")
        address_line2 = request.POST.get("address_line2")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")
        country = request.POST.get("country", "India")
        is_default = request.POST.get("is_default") == "on"
        if not (full_name and phone and address_line1 and city and state and pincode):
            messages.error(request, "Please fill in all required fields.")
            return redirect("edit_address", address_id=address.id)

        if is_default:
            Address.objects.filter(user=request.user, is_default=True).exclude(id=address.id).update(is_default=False)

        address.full_name = full_name
        address.phone = phone
        address.address_line1 = address_line1
        address.address_line2 = address_line2
        address.city = city
        address.state = state
        address.pincode = pincode
        address.country = country
        address.is_default = is_default
        address.save()

        messages.success(request, "Address updated successfully!")
        return redirect("add_address")

    return render(request, "user/address_edit.html", {"address": address})
def delete_address(request, address_id):
    address = Address.objects.get( id=address_id, user=request.user)

    address.delete()
    messages.success(request, "Address deleted successfully!")

    return redirect("add_address")


def subcategory_list(request):
    subcategories = SubCategory.objects.all()
    return render(request, "user/subcategory_list.html", {
        "subcategories": subcategories
    })

def products_by_subcategory(request, sub_id):
    subcategory = SubCategory.objects.get(id=sub_id)
    products = Product.objects.filter(subcategory=subcategory)

    return render(request, "user/products_by_subcategory.html", {
        "subcategory": subcategory,
        "products": products
    })


@role_required('customer', '/user/login')
def order_page(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    total = sum(item.price * item.quantity for item in cart_items)

    return render(request, "user/order.html", {
        "checkout_type": "cart",
        "cart_items": cart_items,
        "total": total,
    })




@role_required('customer', '/user/login')
def place_order(request):
    if request.method == "POST":
        cart_items = Cart.objects.filter(user=request.user)
        address_id = request.POST.get('address_id')
        if not address_id:
            messages.error(request, "Please select a shipping address.")
            return redirect("order_page")

        order = Order.objects.create(
            user=request.user,
            total_amount=0,
            address_id=address_id
        )

        total = 0
        for item in cart_items:
            qty = int(request.POST.get(f'quantities[{item.id}]', 1))
            total += item.price * qty
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=qty,
                price=item.price
            )
            item.product.stock -= qty
            item.product.save()

        order.total_amount = total
        order.save()
        cart_items.delete()

    return redirect('order_success')



@role_required('customer', '/user/login')
def buy_now(request, slug):
    product = Product.objects.get(slug=slug)
    if product.stock < 1:
        messages.error(request, "Product is out of stock.")
        return redirect("single", slug=slug)
    request.session["buy_now_product_id"] = product.id
    return redirect("order_page_buy_now")


@role_required('customer', '/user/login')
def order_page_buy_now(request):
    product_id = request.session.get("buy_now_product_id")
    if not product_id:
        return redirect("shop")

    product = Product.objects.get(id=product_id)

    return render(request, "user/order.html", {
        "checkout_type": "buynow",
        "product": product,
        "total": product.price,
    })


@role_required('customer', '/user/login')
def place_order_buy_now(request):
    if request.method == "POST":
        product_id = request.session.get("buy_now_product_id")
        product = Product.objects.get(id=product_id)
        address_id = request.POST.get("address_id")
        if not address_id:
            messages.error(request, "Please select a shipping address.")
            return redirect("order_page_buy_now")

        if product.stock < 1:
            messages.error(request, "Out of stock.")
            return redirect("shop")

        order = Order.objects.create(
            user=request.user,
            total_amount=product.price,
            address_id=address_id
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            price=product.price,
            quantity=1
        )

        product.stock -= 1
        product.save()
        del request.session["buy_now_product_id"]

    return redirect("order_success")


@role_required('customer', '/user/login')
def order_details(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, "user/order_details.html", {
        "order": order,
        "order_items": order_items
    })


@role_required('customer', '/user/login')
def order_success(request):
    latest_order = Order.objects.filter(user=request.user).order_by('-order_date').first()
    return render(request, "user/order_success page.html", {"order": latest_order})



@role_required('customer', '/user/login')
def order_history(request):


    status_filter = request.GET.get("status", "")

    orders = Order.objects.filter(user=request.user).order_by("-order_date")

    filtered_orders = []

    for order in orders:
        items = OrderItem.objects.filter(order=order)

        # Apply status filtering
        if status_filter:
            items = items.filter(status=status_filter)

        if not items.exists():
            continue

        # Attach items
        order.items = items

        # --- CALCULATE OVERALL ORDER STATUS ---
        statuses = list(items.values_list("status", flat=True))

        if "Cancelled" in statuses:
            order.status = "Cancelled"
        elif all(s == "Delivered" for s in statuses):
            order.status = "Delivered"
        elif "Shipped" in statuses:
            order.status = "Shipped"
        else:
            order.status = "Pending"

        filtered_orders.append(order)

    return render(request, "user/order_item.html", {
        "orders": filtered_orders,
        "selected_status": status_filter})

@role_required('customer', '/user/login')
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    items = OrderItem.objects.filter(order=order)

    # Do not allow cancellation if delivered
    if all(item.status == "Delivered" for item in items):
        messages.error(request, "Delivered orders cannot be cancelled.")
        return redirect("order_item", order_id=order.id)

    # Cancel each item & restock
    for item in items:
        if item.status != "Cancelled":
            item.status = "Cancelled"
            item.product.stock += item.quantity
            item.product.save()
            item.save()

    # Update order status
    order.status = "Cancelled"
    order.save()

    messages.success(request, "Your order has been cancelled.")

    return redirect("order_item")

def order_details(request, order_id):
    # Get the order
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Get all items for the order
    items = OrderItem.objects.filter(order=order)

    # Attach items to order for template
    order.items = items

    # Calculate subtotal
    order.subtotal = sum(item.price * item.quantity for item in items)

    # Example shipping & tax
    order.shipping_cost = 40
    order.tax_amount = round(order.subtotal * 0.05, 2)
    order.total_amount = order.subtotal + order.shipping_cost + order.tax_amount

    # Overall status
    statuses = list(items.values_list("status", flat=True))

    if all(s == "Delivered" for s in statuses):
        order.status = "Delivered"
    elif "Cancelled" in statuses:
        order.status = "Cancelled"
    elif "Shipped" in statuses:
        order.status = "Shipped"
    else:
        order.status = "Pending"

    # 👉 Fetch the shipping address (VERY IMPORTANT)
    shipping_address = order.address   # this gives full Address object

    return render(request, "user/view_details.html", {
        "order": order,
        "shipping_address": shipping_address,   # pass to template
    })

#for profile
@role_required('customer', '/user/login')
def profile(request):
    user = request.user

    # All orders by user
    orders = Order.objects.filter(user=user).order_by('-order_date')
    total_orders = orders.count()

    # Calculate pending orders from OrderItem (not Order)
    pending_orders = 0
    for order in orders:
        if OrderItem.objects.filter(order=order, status="Pending").exists():
            pending_orders += 1

    # Recent 5 orders
    recent_orders = orders[:5]

    # Wishlist
    wishlist_items = Wishlist.objects.filter(user=user)
    wishlist_count = wishlist_items.count()

    # Cart
    cart_count = Cart.objects.filter(user=user).count()

    # Recently Viewed products
    recently_viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed = Product.objects.filter(id__in=recently_viewed_ids)

    # Addresses
    addresses = Address.objects.filter(user=user)

    # Customer Profile
    user_profile = Customer.objects.filter(user=user).first()

    return render(request, 'user/profile.html', {
        'orders': orders,
        'recent_orders': recent_orders,
        'wishlist_items': wishlist_items,
        'recently_viewed': recently_viewed,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
        'addresses': addresses,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'loyalty_points': 30,
        'user_profile': user_profile,
    })


@role_required('customer', '/user/login')
def update_profile(request):
    if request.method == "POST":
        user = request.user

        # Update user fields
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.phone_number = request.POST.get("phone")  # <-- FIXED
        user.save()

        # Update customer address
        customer, created = Customer.objects.get_or_create(user=user)
        customer.address = request.POST.get("address", customer.address)
        customer.save()

        messages.success(request, "Profile updated successfully!")

    return redirect('profile')


@role_required('customer', '/user/login')
def change_password(request):
    if request.method == "POST":
        old = request.POST.get("old_password")
        new1 = request.POST.get("new_password1")
        new2 = request.POST.get("new_password2")

        if not request.user.check_password(old):
            messages.error(request, "Old password is incorrect.")
            return redirect('profile')

        if new1 != new2:
            messages.error(request, "New passwords do not match.")
            return redirect('profile')

        request.user.set_password(new1)
        request.user.save()

        messages.success(request, "Password changed successfully!")
        return redirect('login')

    return redirect('profile')

@role_required('customer', '/user/login')
def delete_account(request):
    user = request.user

    if request.method == "POST":
        # Delete customer profile if exists
        try:
            user.customer_profile.delete()
        except:
            pass

        # Delete addresses
        user.addresses.all().delete()

        # Delete wishlist
        Wishlist.objects.filter(user=user).delete()

        # Delete cart
        Cart.objects.filter(user=user).delete()

        # Delete orders and items
        user.order_set.all().delete()

        # Finally delete the user account
        user.delete()

        messages.success(request, "Your account has been deleted successfully.")
        return redirect('home')

    return render(request, "user/delete_confirmation.html")

def contact(request):
    return render(request,'user/contact.html')