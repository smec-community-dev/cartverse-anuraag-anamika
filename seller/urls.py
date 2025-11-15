from django.urls import path

from . import views

urlpatterns=[
    path('register/',views.seller_register,name='seller_register'),
    path('login/',views.seller_login,name='seller_login'),
    path('seller_dashboard/',views.seller_dashboard),
    path('seller_product/',views.seller_product),
    path('add_product/',views.add_product),
    path('order_products/',views.order_products),
    path('edit_product/',views.seller_editproduct)
]