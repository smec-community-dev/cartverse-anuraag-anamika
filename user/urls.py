from django.urls import path

from . import views



urlpatterns=[
    path('register/',views.user_register,name='register'),
    path('login/', views.user_login, name='login'),
    path('list/',views.product_list,name='home'),
    # path('single/<slug:slug>',views.single_product,name='single')
]