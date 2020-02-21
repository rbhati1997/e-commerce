from celery.task import task
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from django.core.paginator import Paginator

from .helper import seller_ordered_products
from .models import Product, Cart, DeliveryAddress, Order, CartCheckout, MyUser, OrderSeller, CartItem
from django.conf import settings  # new
from shop.tasks import create_seller_order


class Payment(TemplateView):
    """
    Class to define payment page.
    """
    template_name = 'payment.html'

    # delivery_address_id = request.session.get('delivery_address_id')
    # delivery_address = DeliveryAddress.objects.filter(pk=delivery_address_id)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


def product_grid(request):
    """
    Function to show a grid of products.
    :param request:
    """
    user = MyUser.objects.get(user_id=request.user.id)
    if user.user_type == 'C':
        product_list = Product.objects.all()
        if 'search' in request.GET:
            search_term = request.GET['search']
            product_list = product_list.filter(name__icontains=search_term)
        paginator1 = Paginator(product_list, 3)
        page_number = request.GET.get('page')
        if page_number:
            products = paginator1.get_page(page_number)
        else:
            products = paginator1.get_page(1)
    else:
        products = Product.objects.filter(store__seller_user=user)

    context = {
        "user": user,
        'products': products,
        'grid_view': 'grid_view'
    }

    return render(request, 'product_grid.html', context)


def product_detail(request, pk):
    """
    Function shows detail of a product.
    :param request:
    :param pk:
    """
    user = MyUser.objects.get(user_id=request.user.id)
    product = Product.objects.get(pk=pk)
    context = {
        'product': product,
        'user': user
    }
    return render(request, 'product_detail1.html', context)


def add_product_cart(request, product_id=None):
    """
    Function to add product on cart.
    :param request:
    :param product_id:
    :return:Products which added to cart by user.
    """

    price = 0
    user = MyUser.objects.get(pk=request.user.id)

    if product_id > 0:
        product = Product.objects.get(pk=product_id)
        cart = Cart.objects.filter(customer_user=user)

        if cart:
            CartItem.objects.create(product=product, cart=cart[0])
        else:
            cart = Cart.objects.create(customer_user=user)
            CartItem.objects.create(product=product, cart=cart)

    cart_product_list = []

    for cart_product in CartItem.objects.all():
        price += int(cart_product.product.price)
        cart_product_list.append(cart_product)
    context = {
        "cart_product": cart_product_list,
        "cart_products_price": price
    }
    return render(request, 'cart1.html', context)


def remove_product_cart(request, product_id):
    """
    Function to remove product from cart.
    :param request:
    :param product_id:
    """
    # import pdb;pdb.set_trace()
    CartItem.objects.get(pk=product_id).delete()
    return HttpResponseRedirect(reverse('product_cart', args=[0]))


def checkout(request):
    """
    Function to checkout cart products.
    :param request:
    """

    price = 0
    user = MyUser.objects.get(pk=request.user.id)

    if request.method == "POST":
        full_name = request.POST['firstname']
        address = request.POST['address']
        email = request.POST['email']
        postal_code = request.POST['zip']
        city = request.POST['city']
        delivery_address = DeliveryAddress.objects.create(customer_user=user, full_name=full_name, address=address,
                                                          email=email, postal_code=postal_code, city=city)
        request.session['delivery_address_id'] = delivery_address.id
        return HttpResponseRedirect(reverse('payment_page'))
    cart_product_list = CartItem.objects.all()
    for cart in cart_product_list:
        price += int(cart.product.price)
    context = {
        "cart_product": cart_product_list,
        "cart_products_price": price
    }
    return render(request, 'checkout.html', context)


def add_orders(request, order_id=None):
    """
    Function to add order.
    :param order_id:
    :param request:
    """

    user = MyUser.objects.get(user_id=request.user.id)
    if user.user_type == 'C':
        cart_items = CartItem.objects.filter(cart__customer_user=user)
        delivery_address = DeliveryAddress.objects.get(pk=request.session.get('delivery_address_id'))

        if not order_id:
            order = Order.objects.create(customer_user=user, delivery_address=delivery_address)
            for cart_item in cart_items:
                order.product.add(cart_item.product)
                order.save()

        orders = Order.objects.all()
        return render(request, 'orders.html', {"order": orders})

    else:
        orders = seller_ordered_products(user)

        context = {
            'user': user,
            'products': orders
        }
        return render(request, 'product_grid.html', context)


def delete_orders(request, order_id=None):
    """
    Function to delete order.
    :param order_id:
    :param request:
    """
    if order_id:
        order = Order.objects.get(pk=order_id)
        order.delete()
    else:
        Order.objects.all().delete()
    return HttpResponseRedirect(reverse('orders_id', args=[1]))


def order_detail(request, order_id):
    """
    Function shows the detail of order.
    :param request:
    :param order_id:
    """

    price = 0
    order = Order.objects.get(pk=order_id)
    user = MyUser.objects.get(user_id=request.user.id)
    products = order.product.all()
    product_list = []
    for product in products:
        product_list.append(product)
    for cart_product in product_list:
        price += int(cart_product.price)
    context = {
        "cart_product": product_list,
        "cart_products_price": price,
        "order_detail": "order detail",
        "user": user
    }
    return render(request, 'cart1.html', context)


def product_add(request):
    """
    Fuction to add product.
    :param request:
    :return:
    """
    return render(request, 'product_add.html')


def contact_us(request):
    """
    Fuction to show contact page.
    :param request:
    :return:
    """
    return render(request, 'contact1.html')
