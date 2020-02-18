from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from .models import Product, Cart, CustomUser, DeliveryAddress, Order, CartCheckout


class Home(TemplateView):
    template_name = 'product_detail1.html'


def product_grid(request):
    product_list = Product.objects.all()
    if 'search' in request.GET:
        search_term = request.GET['search']
        product_list = product_list.filter(name__icontains=search_term , category__icontains=search_term, description__icontains=search_term)
    paginator1 = Paginator(product_list, 3)
    page_number = request.GET.get('page')
    if page_number:
        product = paginator1.get_page(page_number)
    else:
        product = paginator1.get_page(1)
    return render(request, 'product_grid.html', {'products': product})


def product_detail(request, pk):

    product = Product.objects.get(pk=pk)
    return render(request, 'product_detail1.html', {'product': product})


def add_product_cart(request, product_id=None):
    """
    Function to add product on cart.
    :param request:
    :param product_id:
    :return:Products which added to cart by user.
    """
    price = 0
    user = User.objects.get(pk=request.user.id)
    if product_id > 0:
        product = Product.objects.get(pk=product_id)
        cart_product = Cart.objects.create(customer_user=user)
        cart_product.product.add(product)
    cart_product_list = Product.objects.filter(cart__customer_user_id =user.id)
    for cart_product in cart_product_list:
        price += int(cart_product.price)
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
    product = Product.objects.get(pk=product_id)
    product.cart_set.all()[0].delete()
    return HttpResponseRedirect(reverse('product_cart', args=[0]))


def checkout(request):
    """
    Function to checkout cart products.
    :param request:
    :return:
    """

    user = User.objects.get(pk=request.user.id)
    if request.method == "POST":
        full_name = request.POST['firstname']
        address = request.POST['address']
        email = request.POST['email']
        postal_code = request.POST['zip']
        city = request.POST['city']
        delivery_address = DeliveryAddress.objects.create(customer_user=user, full_name=full_name, address=address, email=email, postal_code=postal_code, city=city)
        request.session['delivery_address_id'] = delivery_address.id
        return HttpResponseRedirect(reverse('orders'))
    return render(request, 'checkout.html')


def add_orders(request):
    """
    Function to add order.
    :param request:
    :return:
    """
    price = 0
    user = User.objects.get(pk=request.user.id)
    carts = Cart.objects.filter(customer_user=user)
    cart_checkout = CartCheckout.objects.create()
    cart_checkout.cart.add(*list(carts))
    cart_checkout.save()
    delivery_address_id = request.session.get('delivery_address_id')
    delivery_address = DeliveryAddress.objects.get(pk=delivery_address_id)
    Order.objects.create(customer_user=user, delivery_address=delivery_address, cart=cart_checkout)
    for cart_product in cart_checkout.cart.all():
        product_price = cart_product.product.all()[0].price
        price += int(product_price)
    orders = Order.objects.all()
    context = {
        "order": orders,
        'price': price,
    }

    return render(request, 'orders.html', context=context)


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