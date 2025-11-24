from django.urls import path

from . import views



urlpatterns=[
    path('register/',views.user_register,name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('main/',views.user_home,name='user_home'),
    path('category/',views.subcategory,name='category'),
    path('subcategory/<slug:slug>',views.subcategory,name='subcategory'),
    path('explore_products/<slug:slug>',views.explore_products,name='explore'),
    path('about/',views.about,name='about'),
    path('single/<slug:slug>',views.single_products,name='single'),
    path('add_wishlist/<slug:slug>',views.add_wishlist,name='add_wishlist'),
    path('view_wishlist',views.view_wishlist,name='wishlist'),
    path('remove_wishlist/<slug:slug>',views.remove_wishlist,name='remove_wishlist'),
    path('cart/',views.cart,name='cart'),
    path('add_cart/<slug:slug>',views.add_cart,name='add_cart'),
    path('remove_cart/<int:cart_id>',views.remove_cart,name='remove_cart'),
    path('update_quantity/<int:cart_id>/', views.update_quantity, name='update_quantity'),

    path("order/", views.order_page, name="order_page"),
    path("place-order/", views.place_order, name="place_order"),
    path("buy-now/<slug:slug>/", views.buy_now, name="buy_now"),
    path("order_page_buy_now/",views.order_page_buy_now,name='order_page_buy_now'),
    path('place_order_buy_now/',views.place_order_buy_now,name='place_order_buy_now'),
     path('orders/', views.order_history, name='order_item'),
    path('review/<int:product_id>',views.add_review,name='add_review'),
    path('cancel_order/<int:order_id>',views.cancel_order,name='cancel_order'),
    path('view_details/<int:order_id>',views.order_details,name='view_detail'),

    path('add_address/',views.add_address,name='add_address'),
    path('order_success/',views.order_success,name='order_success'),
    path('edit_address/<int:address_id>',views.edit_address,name='edit_address'),
    path('delete_address/<int:address_id>', views.delete_address, name='delete_address'),


    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
   path('delete_account/', views.delete_account, name='delete_account'),

    path('contact/',views.contact,name='contact'),
    path('razorpay/create-order/', views.create_razorpay_order, name='razorpay_create_order'),
    path('razorpay/verify-payment/', views.verify_payment, name='razorpay_verify_payment'),
]