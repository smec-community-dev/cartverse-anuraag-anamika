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
    path("users/add_user/", views.add_user, name="add_user"),
    path("products/", views.admin_products, name="admin_products"),
    path("products/<int:id>/", views.product_detail_view, name="product-detail"),
path("products/<int:id>/delete/", views.delete_product_view, name="delete-product"),
path("seller/<int:id>/", views.admin_seller_profile, name="admin-seller-profile"),
path("products/seller/<int:seller_id>/", views.admin_products_by_seller, name="admin-products-by-seller"),
path("seller/<int:id>/warning/", views.admin_send_warning, name="admin-send-warning"),
path("seller/<int:id>/suspend/", views.admin_suspend_seller, name="admin-suspend-seller"),
path("orders/", views.admin_orders_view, name="admin-orders"),
path("orders/<int:order_id>/", views.admin_order_detail_view, name="admin-order-detail"),
path("orders/<int:order_id>/delete/", views.admin_order_delete_view, name="admin-order-delete"),
path("sellers/", views.admin_sellers_view, name="admin_sellers"),

path("sellers/<int:seller_id>/", views.admin_seller_detail, name="admin-seller-detail"),
path("sellers/<int:seller_id>/delete/", views.admin_seller_delete, name="admin-seller-delete"),

    path("categories/", views.admin_category_view, name="admin-categories"),
    path("subcategories/", views.view_subcategories, name="admin-subcategories"),

    # Create
    path("category/add/", views.add_category, name="add-category"),
    path("subcategory/add/", views.add_subcategory, name="add-subcategory"),

    # Delete
    path("category/delete/<int:id>/", views.delete_category, name="delete-category"),
    path("subcategory/delete/<int:id>/", views.delete_subcategory, name="delete-subcategory"),

path("categories/edit/<int:pk>/", views.edit_category, name="edit-category"),

    path("subcategories/edit/<int:pk>/", views.edit_subcategory, name="edit-subcategory"),

path("profile/", views.admin_profile, name="admin-profile"),

path("profile/update/", views.update_profile, name="update-profile"),
path("profile/change-password/", views.change_password, name="change-password"),







]