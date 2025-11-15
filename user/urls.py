from django.urls import path

from . import views



urlpatterns=[
    path('register/',views.user_register,name='register'),
    path('login/', views.user_login, name='login'),
    path('',views.user_home,name='home'),
    path('list/',views.list_products,name='product_list'),
    path('single/<slug:slug>',views.single_product,name='single')
]