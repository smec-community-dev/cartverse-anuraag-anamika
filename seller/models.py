from django.db import models

# Create your models here.
from core.models import User
from core.models import SubCategory,Category

class Seller(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=200)
    location = models.TextField()

    def __str__(self):
        return self.shop_name

#hai
#byebye
class Product(models.Model):

    product_name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.FloatField()
    stock = models.IntegerField()
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name


#
# # ✅ VariantAttribute — created by seller (e.g., “Size”, “Color”, “Material”)
# class VariantAttribute(models.Model):
#     seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#
#     def __str__(self):
#         return f"{self.name}"
#
#
# # ✅ VariantOption — the possible values of a VariantAttribute (e.g., “Size” → “M”)
# class VariantOption(models.Model):
#     attribute = models.ForeignKey(VariantAttribute, on_delete=models.CASCADE, related_name="options")
#     value = models.CharField(max_length=100)
#
#     def __str__(self):
#         return f"{self.attribute.name}: {self.value}"
#

# ✅ ProductVariant — specific combination of options for a product (e.g., “Size=M, Color=Red”)
# class ProductVariant(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
#     options = models.ManyToManyField(VariantOption, related_name="product_variants")
#     price = models.FloatField()
#     stock = models.IntegerField()
#
#     def __str__(self):
#
#         return f"{self.product.product_name}"
#

# ✅ ProductImage — can belong to either the product or a specific variant
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to='product_images/')

    def __str__(self):

        return f"Image of {self.product.product_name}"