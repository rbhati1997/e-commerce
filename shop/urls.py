from django.urls import path
from .views import product_detail, Home, product_grid, add_product_cart, remove_product_cart

urlpatterns = [
    path('home/', Home.as_view(), name='home_page'),
    path('products/', product_grid, name='product_grid'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('cart/<int:product_id>/', add_product_cart, name='product_cart'),
    path('remove_cart_product/<int:product_id>/', remove_product_cart, name='remove_product_cart')
    # path('products/<int:category_id>/', product_grid, name='product_list'),


]

