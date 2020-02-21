from django.contrib import admin
from .models import Product, Cart, Order, DeliveryAddress, OrderLine, Review, Store, MyUser, OrderSeller, CartItem
from django.contrib.admin.models import LogEntry


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'available', 'stock', 'created_at', 'updated_at']


class CartAdmin(admin.ModelAdmin):
    list_display = ['customer_user']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer_user', 'quantity', 'delivery_address']


class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ['customer_user', 'address', 'postal_code', 'city']


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['customer_user', 'product', 'rate', 'review']


# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = ['first_name', 'date_joined', 'user_type']


# admin.site.register(Category)
admin.site.register(LogEntry)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
# admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(DeliveryAddress, DeliveryAddressAdmin)
admin.site.register(OrderLine)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Store)
admin.site.register(MyUser)
admin.site.register(OrderSeller)
admin.site.register(CartItem)
