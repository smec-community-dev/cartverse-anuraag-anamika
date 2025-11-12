
from django.db import models
# Create your models here.
from core.models import User

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('seller.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField()

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey("seller.Product", on_delete=models.CASCADE)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey("seller.Product", on_delete=models.CASCADE)
    rating = models.IntegerField()
    review_comment = models.TextField()
    review_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.rating}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    address = models.CharField(max_length=255)
    order_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey("seller.Product", on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity}"



