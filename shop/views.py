from celery.task import task
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from .forms import DeliveryAddressForm, ProductForm
from .helper import seller_ordered_products, global_search_bar, total_price
from .models import Product, Cart, DeliveryAddress, Order, MyUser, CartItem, Store
from django.conf import settings

import twilio
import twilio.rest


class Payment(TemplateView):
    """
    Class to define payment page.
    """
    template_name = 'payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


def product_grid(request):
    """
    Function to show a grid of products.
    :param request:
    """
    user = get_object_or_404(MyUser, user_id=request.user.id)
    # When user type is customer.
    if user.user_type == 'C':
        product_list = Product.objects.all()
        if 'search' in request.GET:
            product_list = global_search_bar(request.GET)
        paginator1 = Paginator(product_list, 3)
        page_number = request.GET.get('page')
        if page_number:
            products = paginator1.get_page(page_number)
        else:
            products = paginator1.get_page(1)
    # When user type is seller.
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

    user = MyUser.objects.get(pk=request.user.id)

    if product_id > 0:
        product = Product.objects.get(pk=product_id)
        cart = Cart.objects.filter(customer_user=user)

        if cart:
            CartItem.objects.create(product=product, cart=cart[0])
        else:
            cart = Cart.objects.create(customer_user=user)
            CartItem.objects.create(product=product, cart=cart)

    cart_items = CartItem.objects.all()
    price = total_price(cart_items)

    if 'search' in request.GET:
        cart_items = global_search_bar(request.GET)

    context = {
        "cart_product": cart_items,
        "cart_products_price": price,
        'user':user
    }
    return render(request, 'cart1.html', context)


def remove_product_cart(request, product_id):
    """
    Function to remove product from cart.
    :param request:
    :param product_id:
    """
    CartItem.objects.get(pk=product_id).delete()
    return HttpResponseRedirect(reverse('product_cart', args=[0]))


def checkout(request):
    """
    Function to checkout cart products and create delivery object.
    :param request:
    """

    user = MyUser.objects.get(pk=request.user.id)

    if request.method == "POST":
        form = DeliveryAddressForm(request.POST)
        if form.is_valid():
            delivery_address = form.save()
        request.session['delivery_address_id'] = delivery_address.id
        return HttpResponseRedirect(reverse('payment_page'))
    cart_product_list = CartItem.objects.all()
    price = total_price(cart_product_list)
    form = DeliveryAddressForm(initial={'customer_user': user})
    context = {
        "cart_product": cart_product_list,
        "cart_products_price": price,
        "form": form,
        'user':user
    }
    return render(request, 'checkout.html', context)


def add_orders(request, order_id=None):
    """
    Function to add order.
    :param order_id:
    :param request:
    """
    user = MyUser.objects.get(user_id=request.user.id)
    # When user type is customer.
    if user.user_type == 'C':
        cart_items = CartItem.objects.filter(cart__customer_user=user)
        delivery_address = DeliveryAddress.objects.get(pk=request.session.get('delivery_address_id'))

        if not order_id:
            order = Order.objects.create(customer_user=user, delivery_address=delivery_address)
            for cart_item in cart_items:
                order.product.add(cart_item.product)
                order.save()
                cart_item.delete()
        orders = Order.objects.all()
        return render(request, 'orders.html', {"order": orders, "user": user})

    # When user type is seller.
    else:
        orders = seller_ordered_products(user)
        context = {
            'user': user,
            'order': orders
        }

        return render(request, 'orders.html', context)


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
    user = MyUser.objects.get(user_id=request.user.id)
    price = 0

    order = Order.objects.get(pk=order_id)
    products = order.product.all()
    product_list = []

    for product in products:
        if user.user_type == 'C':
            product_list.append(product)
        elif user == product.store.seller_user:
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


def contact_us(request):
    """
    Function to show contact page.
    :param request:
    :return:
    """
    user = MyUser.objects.get(user_id=request.user.id)
    return render(request, 'contact1.html', {'user':user})


def send_msg(request, order_id):
    """
    Function to send message to customer.
    :param request:
    :param order_id:
    :return:Message
    """
    order = Order.objects.get(pk=order_id)
    number = order.delivery_address.number
    body = "your order id-{} is accepted, Thank you" \
           "from BIGDADDYSHOP".format(order_id)
    client = twilio.rest.Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    client.messages.create(
        body=body,
        to='+91' + number,
        from_=settings.TWILIO_PHONE_NUMBER
    )
    return HttpResponseRedirect(reverse('orders'))


def product_add(request):
    """
    Function to add product.
    :param request:
    :return:
    """
    user = MyUser.objects.get(user_id=request.user.id)
    # store = Store.objects.get(seller_user=user)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("product_grid"))

    # form = ProductForm(initial={'store': store})
    form = ProductForm()
    context = {'form': form, 'user':user}
    return render(request, 'product_add.html', context)
