from django.urls import path

from . import views



urlpatterns=[
    path('register/',views.user_register,name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('main/',views.product_list,name='user_home'),
    path('single/<slug:slug>',views.single_products,name='single'),
    path('add_wishlist/<slug:slug>',views.add_wishlist,name='add_wishlist'),
    path('view_wishlist',views.view_wishlist,name='wishlist'),
    path('remove_wishlist/<slug:slug>',views.remove_wishlist,name='remove_wishlist'),
    path('cart/',views.cart,name='cart'),
    path('add_cart/<slug:slug>',views.add_cart,name='add_cart'),
    path('remove_cart/<int:cart_id>',views.remove_cart,name='remove_cart'),
    path('update_quantity/<int:cart_id>/', views.update_quantity, name='update_quantity'),
    # path('categories/<int:id>',views.categories,name='category'),
    path("order/", views.order_page, name="order_page"),
    path("place-order/", views.place_order, name="place_order"),
    path("buy-now/<slug:slug>/", views.buy_now, name="buy_now"),
    path("place-order/", views.place_order, name="place_order"),
    path("buy-now/<slug:slug>/", views.buy_now, name="buy_now"),
    path('add_address/',views.add_address,name='add_address'),
    path('order_success/',views.order_success,name='order_success'),
    path('edit_address/<int:address_id>',views.edit_address,name='edit_address'),
    path('delete_address/<int:address_id>', views.delete_address, name='delete_address'),


]