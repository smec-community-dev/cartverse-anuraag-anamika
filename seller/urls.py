from django.urls import path

from . import views

urlpatterns=[
    path('register/',views.seller_register,name='seller_register'),
    path('login/',views.seller_login,name='seller_login'),
    path('seller_dashboard/',views.seller_dashboard),
    path('seller_product/',views.seller_product,name='seller_product'),
    path('add_product/',views.add_product),
    path('order_products/',views.order_products),
    path('edit_product/<int:id>/<slug:slug>/',views.seller_editproduct),
    path('delete_product/<int:id>/<slug:slug>/',views.seller_delete_product),
    path('logout/',views.seller_logout,name='seller_logout'),
    path('single_orderproduct/<slug:product_slug>/',views.single_order_product,name='single_order'),
    path('seller_profile/',views.seller_profile,name='seller_profile')
]