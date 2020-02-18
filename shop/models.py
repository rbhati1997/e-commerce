from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
import uuid


class CustomUser(User):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    TYPE_CHOICE = (
        ('A', 'Admin'),
        ('S', 'Seller'),
        ('C', 'Customer')
    )
    user_type = models.CharField(max_length=2, choices=TYPE_CHOICE, default='A')

    def __str__(self):
        return '{},{}'.format(self.user_type, self.first_name)


# class Category(models.Model):
#     uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
#     seller_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='category_seller_user')
#     name = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.name


class Store(models.Model):
    seller_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store_seller_user')

    def save(self, **kwargs):
        if self.seller_user.user_type == 'C':
            raise ValidationError({'error': 'Customer not able to choose a store.'})
        super().save(**kwargs)

    def __str__(self):
        return self.seller_user.first_name


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
    seller_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_seller_user')
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICE, default=None)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_category')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    image = models.ImageField(upload_to="product_image", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    # def save(self, **kwargs):
    #     if self.seller_user.user_type == 'C':
    #         raise ValidationError({'error': 'Customer not able to create product.'})
    #     super().save(**kwargs)

    def __str__(self):
        return self.name


class Cart(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_customer_user')
    product = models.ManyToManyField(Product)

    # def save(self, **kwargs):
    #     if self.customer_user.user_type == 'S':
    #         raise ValidationError({'error': 'Seller not able to add product in cart.'})
    #     super().save(**kwargs)

    def __int__(self):
        return self.uuid


class CartCheckout(models.Model):
    cart = models.ManyToManyField(Cart)


class DeliveryAddress(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_customer_user')
    full_name = models.CharField(max_length=250, null=True)
    address = models.CharField(max_length=250, null=True)
    email = models.EmailField(null=True)
    postal_code = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.address


class Order(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_customer_user')
    cart = models.ForeignKey(CartCheckout, on_delete=models.CASCADE, related_name='order_cart', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_product', blank=True, null=True)
    quantity = models.IntegerField(default=0)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True, null=True)

    # def save(self, **kwargs):
    #     if self.customer_user.user_type == 'S':
    #         raise ValidationError({'error': 'Seller not able to add product in cart.'})
    #
    #     if self.cart and self.product:
    #         raise ValidationError({'error': 'Please provide any one between cart_id and product.'})
    #     elif self.cart and not self.product:
    #         if self.quantity > 0:
    #             raise ValidationError({'error': 'Cant give quantity when purchasing from cart.'})
    #         super().save(**kwargs)
    #     elif self.product and not self.cart:
    #         super().save(**kwargs)

    def __int__(self):
        return self.uuid


class Review(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_customer_user')
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


class OrderLine(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4().int >> 81, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_line_order')

    def __int__(self):
        return self.uuid


class Blog(models.Model):
    name = models.CharField(max_length=100)
    tagline = models.TextField()

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Entry(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    headline = models.CharField(max_length=255)
    body_text = models.TextField()
    pub_date = models.DateField(auto_now_add=True)
    mod_date = models.DateField(auto_now_add=True)
    authors = models.ManyToManyField(Author)
    number_of_comments = models.IntegerField()
    number_of_pingbacks = models.IntegerField()
    rating = models.IntegerField()

    def __str__(self):
        return self.headline
