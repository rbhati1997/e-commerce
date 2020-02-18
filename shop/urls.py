from django.urls import path
from .views import product_detail, Home, product_grid, add_product_cart, remove_product_cart, product_add, contact_us, \
    checkout, add_orders, delete_orders, order_detail

urlpatterns = [
    path('home/', Home.as_view(), name='home_page'),
    path('products/', product_grid, name='product_grid'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('product_add', product_add, name='product_add'),
    path('cart/<int:product_id>/', add_product_cart, name='product_cart'),
    path('carts/<int:order_id>/', order_detail, name='order_detail'),
    path('remove_cart_product/<int:product_id>/', remove_product_cart, name='remove_product_cart'),
    path('contact_us/', contact_us, name="contact_us"),
    path('checkout/', checkout, name="checkout"),
    path('orders/', add_orders, name="orders"),
    path('orders/<int:order_id>', add_orders, name="orders_id"),
    path('delete_orders/<int:order_id>', delete_orders, name="delete_order"),
    path('delete_orders/', delete_orders, name="delete_orders"),

]

