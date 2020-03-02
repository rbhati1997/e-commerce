from datetime import datetime
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.http import request
from guardian.shortcuts import assign_perm


class MyUser(AbstractUser):
    TYPE_CHOICE = (
        ('S', 'Seller'),
        ('C', 'Customer')
    )
    user_type = models.CharField(max_length=2, choices=TYPE_CHOICE, default='S')
    is_customer = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("can_message", "Can send message"),
        )

    def __str__(self):
        return self.username


class Store(models.Model):
    seller_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='store_seller_user')

    def __str__(self):
        return self.seller_user.username


class Product(models.Model):
    CATEGORY_CHOICE = (
        ('CLT', 'clothes'),
        ('SH', 'shoes'),
        ('MOB', 'mobiles'),
        ('LAP', 'laptops'),
        ('WTC', 'watches'),
    )
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='product_store', null=True)
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICE, default=None)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    image = models.ImageField(upload_to="product_image", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    customer_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_customer_user')
    created_at = models.DateTimeField(default=datetime.now)

    class Meta:
        permissions = (
            ("can_checkout", "Can checkout"),
        )

    def __int__(self):
        return self.uuid


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        user = kwargs['request'].user
        super(CartItem, self).save(*args)
        assign_perm('view_cartitem', user, self)
        assign_perm('delete_cartitem', user, self)
        return self


class DeliveryAddress(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_customer_user')
    full_name = models.CharField(max_length=250, null=True)
    number = models.CharField(max_length=15, null=True)
    address = models.CharField(max_length=250, null=True)
    email = models.EmailField(null=True)
    postal_code = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.address


class Order(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_customer_user')
    product = models.ManyToManyField(Product, related_name='order_product', blank=True)
    quantity = models.IntegerField(default=0)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.CASCADE, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        user = kwargs['request'].user
        super(Order, self).save(*args)
        assign_perm('view_order', user, self)
        assign_perm('delete_order', user, self)
        return self

    def __int__(self):
        return self.uuid


class Review(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_customer_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.IntegerField(default=10, validators=[MaxValueValidator(10), MinValueValidator(1)])
    review = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.uuid
