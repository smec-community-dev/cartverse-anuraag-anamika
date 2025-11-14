from django.urls import path

from . import views

urlpatterns=[
    path('seller_register/',views.seller_register),
    path('seller_login/',views.seller_login)
]