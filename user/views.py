from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout

from decorators.decorators import role_required
from .models import Customer, Wishlist,Cart,Order,OrderItem,Address
from core.models import User,Category,SubCategory
from seller.models import Product,ProductImage
from django.contrib import messages
from django.core.paginator import Paginator
from decorators.decorators import role_required
from django.db.models import Q


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


def home(request):
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart_count = Cart.objects.filter(user=request.user).count()
    else:
        wishlist_count = 0
        cart_count = 0
    return render(request,'user/home.html',{'count':wishlist_count,'cart':cart_count})


def product_list(request):
        products=Product.objects.prefetch_related('images').all()
        search=request.GET.get('search')
        if search:
            products=products.filter(product_name__icontains=search)
        if request.user.is_authenticated:
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
            cart_count = Cart.objects.filter(user=request.user).count()
        else:
            wishlist_count=0
            cart_count=0
        paginator = Paginator(products, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'user/user_home.html',{"x":page_obj,'count':wishlist_count,'cart':cart_count})

def single_products(request,slug):
    product = Product.objects.prefetch_related('images').get(slug=slug)
    all_images = product.images.all()
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart_count = Cart.objects.filter(user=request.user).count()
    else:
        wishlist_count = 0
        cart_count = 0
    return render(request, 'user/single.html', { 'product': product, 'image': all_images,'count':wishlist_count,'cart':cart_count })


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

@role_required('customer','/user/login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    total = sum(item.price * item.quantity for item in cart_items)

    return render(request, "user/cart.html", {"cart_items": cart_items, "total": total})



@role_required('customer', '/user/login')
def order_page(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")
    total = sum(item.price * item.quantity for item in cart_items)
    return render(request, "user/order.html", {
        "cart_items": cart_items,
        "total": total
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
    return render(request, "user/order_page_single.html", {
        "product": product,
        "total": product.price
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

