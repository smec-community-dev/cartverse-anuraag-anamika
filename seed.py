# import os
# import django
# import random
# from faker import Faker
# from PIL import Image, ImageDraw
# from django.utils.text import slugify
#
# # ------------------- DJANGO SETUP -------------------
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
# django.setup()
#
# from core.models import User, Category, SubCategory
# from seller.models import Seller, Product, ProductImage
# from user.models import Customer, Cart, Order, OrderItem, Wishlist, Review, Address
#
# fake = Faker()
#
# # ------------------- IMAGE GENERATOR -------------------
# def generate_image(path, text):
#     os.makedirs(os.path.dirname(path), exist_ok=True)
#     img = Image.new("RGB", (600, 600), color=(
#         random.randint(50, 200),
#         random.randint(50, 200),
#         random.randint(50, 200)
#     ))
#     draw = ImageDraw.Draw(img)
#     draw.text((30, 30), text, fill="white")
#     img.save(path)
#     return path
#
# # ------------------- DATA DEFINITIONS -------------------
# PRODUCT_DATA = {
#     "Mobiles": ["iPhone 14 Pro Max", "Samsung Galaxy S23 Ultra", "OnePlus 11R", "Vivo V29 Pro", "Realme X7 Max"],
#     "Laptops": ["MacBook Air M2", "HP Pavilion Gaming", "Dell XPS 13", "Lenovo ThinkPad X1", "Asus ROG Strix G15"],
#     "Headphones": ["Sony WH-1000XM5", "JBL Tune 760", "Boat Rockerz 550", "Apple AirPods Pro", "Sennheiser HD450BT"],
#     "Mens Wear": ["Slim Fit Formal Shirt", "Denim Jacket", "Casual Cotton T-Shirt", "Regular Fit Jeans", "Hooded Sweatshirt"],
#     "Womens Wear": ["Floral Kurti", "Georgette Saree", "Crop Top", "Ladies Blazer", "Anarkali Dress"],
#     "Skincare": ["Vitamin C Serum", "Aloe Vera Gel", "Moisturizing Cream", "Sunscreen SPF 50", "Hydrating Face Wash"],
#     "Fitness": ["Yoga Mat", "Dumbbell Set", "Resistance Band", "Treadmill Machine", "Fitness Tracker Watch"]
# }
#
# CATEGORY_MAPPING = {
#     "Electronics": ["Mobiles", "Laptops", "Headphones"],
#     "Fashion": ["Mens Wear", "Womens Wear"],
#     "Beauty": ["Skincare"],
#     "Sports": ["Fitness"]
# }
#
# REVIEW_TEXTS = [
#     "Amazing product, totally worth it!",
#     "Good quality for this price.",
#     "I am not fully satisfied.",
#     "Best purchase of the year!",
#     "Highly recommended!"
# ]
#
# # ------------------- USERS -------------------
# print("Creating Users...")
# roles = ["admin", "seller", "customer"]
# for _ in range(15):
#     User.objects.get_or_create(
#         username=fake.user_name(),
#         defaults={
#             "password": "password123",
#             "phone_number": fake.phone_number(),
#             "role": random.choice(roles)
#         }
#     )
#
# users = list(User.objects.all())
#
# # ------------------- CATEGORIES & SUBCATEGORIES -------------------
# print("Creating Categories & Subcategories...")
# for cat_name in CATEGORY_MAPPING:
#     cat, _ = Category.objects.get_or_create(category_name=cat_name)
#     for sub_name in CATEGORY_MAPPING[cat_name]:
#         SubCategory.objects.get_or_create(category=cat, sub_category_name=sub_name)
#
# categories = list(Category.objects.all())
# subcategories = list(SubCategory.objects.all())
#
# # ------------------- SELLERS -------------------
# print("Creating Sellers...")
# seller_users = [u for u in users if u.role == "seller"]
# sellers = []
#
# for u in seller_users:
#     img_path = f"media/seller_profiles/{u.username}.jpg"
#     generate_image(img_path, u.username)
#
#     seller, _ = Seller.objects.get_or_create(
#         user=u,
#         defaults={
#             "shop_name": fake.company(),
#             "location": fake.address(),
#         }
#     )
#     sellers.append(seller)
#
# # ------------------- PRODUCTS -------------------
# print("Creating Products...")
# products = []
#
# for subcat in subcategories:
#     names = PRODUCT_DATA.get(subcat.sub_category_name, [])
#     if not names:
#         continue
#
#     for name in names:
#         seller = random.choice(sellers)
#         price = random.randint(300, 80000)
#
#         product = Product.objects.create(
#             seller=seller,
#             subcategory=subcat,
#             product_name=name,
#             slug=slugify(name),
#             description=fake.paragraph(),
#             price=price,
#             stock=random.randint(5, 50),
#         )
#
#         # Add 2-4 images
#         for i in range(random.randint(2, 4)):
#             img_path = f"media/products/{product.id}_{i}.jpg"
#             generate_image(img_path, name)
#
#             ProductImage.objects.create(
#                 product=product,
#                 seller=seller,
#                 product_image=f"products/{product.id}_{i}.jpg"
#             )
#
#         products.append(product)
#
# # ------------------- CUSTOMERS -------------------
# print("Creating Customers...")
# customer_users = [u for u in users if u.role == "customer"]
#
# for u in customer_users:
#     path = f"media/profiles/{u.username}.jpg"
#     generate_image(path, u.username)
#
#     Customer.objects.get_or_create(
#         user=u,
#         defaults={
#             "address": fake.address(),
#         }
#     )
#
# # ------------------- ADDRESS -------------------
# print("Creating Addresses...")
# addresses = {}
#
# for cu in customer_users:
#     addr = Address.objects.create(
#         user=cu,
#         full_name=fake.name(),
#         phone=fake.phone_number(),
#         address_line1=fake.street_address(),
#         address_line2=fake.secondary_address(),
#         city=fake.city(),
#         state=fake.state(),
#         pincode=fake.postcode(),
#         country="India",
#         is_default=True,
#     )
#     addresses[cu] = addr
#
# # ------------------- CART ITEMS -------------------
# print("Creating Cart Items...")
# for cu in customer_users:
#     for _ in range(2):
#         Cart.objects.create(
#             user=cu,
#             product=random.choice(products),
#             quantity=random.randint(1, 3),
#             price=random.randint(300, 80000),
#         )
#
# # ------------------- ORDERS & ORDER ITEMS -------------------
# print("Creating Orders...")
# for cu in customer_users:
#     order = Order.objects.create(
#         user=cu,
#         total_amount=random.randint(800, 20000),
#         address=addresses[cu],      # <-- FIXED
#     )
#
#     for _ in range(random.randint(1, 4)):
#         OrderItem.objects.create(
#             order=order,
#             product=random.choice(products),
#             price=random.randint(300, 80000),
#             quantity=random.randint(1, 3),
#             status="Pending",
#         )
#
# # ------------------- WISHLIST -------------------
# print("Creating Wishlists...")
# for cu in customer_users:
#     for _ in range(2):
#         Wishlist.objects.create(
#             user=cu,
#             product=random.choice(products),
#         )
#
# # ------------------- REVIEWS -------------------
# print("Creating Reviews...")
# for cu in customer_users:
#     for _ in range(3):
#         product = random.choice(products)
#         Review.objects.create(
#             user=cu,
#             product=product,
#             rating=random.randint(3, 5),
#             review_comment=random.choice(REVIEW_TEXTS),
#         )
#
# print("✅ Dummy Data Created Successfully!")
