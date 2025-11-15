from django.contrib import admin

from .models import Customer,Cart,Wishlist,Review,Order,OrderItem

admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
