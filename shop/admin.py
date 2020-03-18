from django.contrib import admin
from .models import Product, Cart, Order, DeliveryAddress, Store, MyUser, CartItem

# admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(DeliveryAddress)
admin.site.register(Store)
admin.site.register(MyUser)
admin.site.register(CartItem)