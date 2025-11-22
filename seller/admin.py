from django.contrib import admin

from .models import Seller,Product,ProductImage,Notification

admin.site.register(Seller)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Notification)