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
    path('single_orderproduct/<slug:slug>/',views.single_order_product,name='single_order'),
    path('seller_profile/',views.seller_profile,name='seller_profile'),
    path('seller_change_password/',views.change_password,name='change_password'),
    path('seller_delete/',views.seller_account_delete,name='seller_account_delete'),
    path('seller_profile/',views.seller_profile,name='seller_profile'),
    path('seller_review/<int:product_id>/<slug:slug>/',views.seller_review,name='seller_review'),
    path('seller_notifications/',views.notification_page,name="notifications"),
    path('privacypolicy/',views.privacy),
    path('termsofservice/',views.terms),
 path("api/unread_notifications/", views.api_unread_notifications, name="unread_notifications"),
]


