from django.urls import path
from .views import product_detail, product_grid, add_product_cart, remove_product_cart, product_add, contact_us, \
    checkout, add_orders, delete_orders, order_detail, Payment, send_msg, delete_product

urlpatterns = [
    path('product/cart/checkout/payment/', Payment.as_view(), name='payment_page'),
    path('products/', product_grid, name='product_grid'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('product_add/', product_add, name='product_add'),
    path('delete_product/<int:product_id>/', delete_product, name='delete_product'),
    path('product/<int:product_id>/cart/', add_product_cart, name='product_cart'),
    path('carts/<int:order_id>/', order_detail, name='order_detail'),
    path('remove_cart_product/<int:product_id>/', remove_product_cart, name='remove_product_cart'),
    path('contact_us/', contact_us, name="contact_us"),
    path('product/cart/checkout/', checkout, name="checkout"),
    path('orders/', add_orders, name="orders"),
    path('orders/<int:order_id>/', add_orders, name="orders_id"),
    path('delete_orders/<int:order_id>/', delete_orders, name="delete_order"),
    path('delete_orders/', delete_orders, name="delete_orders"),
    path('send_message/<int:order_id>/accepted_order/', send_msg, name="send_message"),

]


