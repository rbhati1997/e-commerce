from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
import uuid


class MyUser(models.Model):
    TYPE_CHOICE = (
        ('A', 'Admin'),
        ('S', 'Seller'),
        ('C', 'Customer')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=2, choices=TYPE_CHOICE, default='A')

    def __str__(self):
        return self.user_type


class Store(models.Model):
    seller_user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='store_seller_user')

    def save(self, **kwargs):
        if self.seller_user.user_type == 'C':
            raise ValidationError({'error': 'Customer not able to choose a store.'})
        super().save(**kwargs)

    def __str__(self):
        return self.seller_user.user.username


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
    customer_user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='cart_customer_user')
    created_at = models.DateTimeField(default=datetime.now)

    def save(self, **kwargs):
        if self.customer_user.user_type == 'S':
            raise ValidationError({'error': 'Seller not able to add product in cart.'})
        super().save(**kwargs)

    def __int__(self):
        return self.uuid


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)


class CartCheckout(models.Model):
    cart = models.ManyToManyField(Cart)


class DeliveryAddress(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    customer_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='delivery_customer_user')
    full_name = models.CharField(max_length=250, null=True)
    address = models.CharField(max_length=250, null=True)
    email = models.EmailField(null=True)
    postal_code = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.address


class Order(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    customer_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='order_customer_user')
    # cart_item = models.ManyToManyField(CartItem, related_name='order_cart_item', blank=True, null=True)
    product = models.ManyToManyField(Product, related_name='order_product', blank=True)
    quantity = models.IntegerField(default=0)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.CASCADE, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)

    def __int__(self):
        return self.uuid


class OrderLine(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_line_order')

    def __int__(self):
        return self.uuid


class Review(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    customer_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='review_customer_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.IntegerField(default=10, validators=[MaxValueValidator(10), MinValueValidator(1)])
    review = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, **kwargs):
        if self.customer_user.user_type == 'S':
            raise ValidationError({'error': 'Seller not able to give review.'})
        super().save(**kwargs)

    def __int__(self):
        return self.uuid


class OrderSeller(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    product_seller = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_seller.name
