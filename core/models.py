from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

class User(AbstractUser):
    phone_number=models.CharField(max_length=20,blank=True, null=True)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('seller', 'Seller'),
        ('customer', 'Customer')
    ])

    def __str__(self):
        return self.username
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="category_images/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name



class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.sub_category_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.sub_category_name
