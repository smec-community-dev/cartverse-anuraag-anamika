from django.urls import path

from core import views


urlpatterns=[
    path('login/',views.admin_login),
    path('dashboard/',views.admin_dashboard),
    path('users/',views.view_user),
    path("users/<int:user_id>/suspend/", views.suspend_user, name="suspend_user"),
    path("users/<int:user_id>/activate/", views.activate_user, name="activate_user"),
    path("users/<int:user_id>/delete/", views.delete_user, name="delete_user"),
    path("users/<int:user_id>/edit/", views.edit_user, name="edit_user"),
    path("users/<int:user_id>/profile/", views.view_profile, name="user_profile"),
    path("users/<int:user_id>/orders/", views.view_user_orders, name="user_orders"),
    path("users/<int:user_id>/products/", views.view_seller_products, name="seller_products"),
    path("users/<int:user_id>/delete/", views.delete_user, name="delete_user"),






]