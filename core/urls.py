from django.urls import path

from core import views


urlpatterns=[
    path('login/',views.admin_login),
    path('dashboard/',views.admin_dashboard)

]