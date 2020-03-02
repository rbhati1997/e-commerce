from celery.task import task
from django.http import HttpResponseRedirect, HttpResponse
from django.http.request import QueryDict
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from .services import ProductGridService, ProductDetailService, AddProductCartService, RemoveProductCartService, \
    CheckoutService, AddOrderService, DeleteOrderService, OrderDetailService, DeleteProductService, AddProductService, \
    ShowProductCartService, ShowSellerOrderService
from .utils import get_user
from .models import Order, MyUser
from django.conf import settings
from django.contrib.auth.decorators import login_required
import twilio
import twilio.rest
from django.contrib.auth.decorators import permission_required


class Payment(TemplateView):
    """
    Class to define payment page.
    """
    template_name = 'payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


@login_required
def product_grid(request):
    """
    Function to show a grid of products.
    :param request:
    """
    user = get_user(request)
    # Fetching context by executing ProductGridService with given data.
    context = ProductGridService.execute({'user': user, 'get_request': request.GET})
    return render(request, 'product_grid.html', context)


@login_required
def product_detail(request, pk):
    """
    Function shows detail of a product.
    :param request:
    :param pk:
    """
    context = ProductDetailService.execute({'pk': pk, 'request': request})
    if context['permission']:
        return render(request, 'product_detail1.html', context)
    return HttpResponse('Sorry you dont have permission to view this object')


@login_required
@permission_required('shop.add_product', raise_exception=True)
def product_add(request):
    """
    Function to add product.
    :param request:
    :return:
    """
    context = AddProductService.execute({'request': request})
    if context["user"]:
        return render(request, 'product_add.html', context)
    return HttpResponseRedirect(reverse("product_grid"))


@login_required
@permission_required('shop.delete_product', raise_exception=True)
def delete_product(request, product_id):
    """
    Function to delete a product.
    :param product_id:
    :param request:
    """
    user = get_user(request)
    context = DeleteProductService.execute({'user': user, 'product_id': product_id})
    if context['permission']:
        context['product'].delete()
        return HttpResponseRedirect(reverse("product_grid"))
    return HttpResponse('Sorry you dont have permission to delete this object:-{}'.format(product_id))


@login_required
@permission_required('shop.add_cart', raise_exception=True)
def add_product_cart(request, product_id=None):
    """
    Function to add product on cart.
    :param request:
    :param product_id:
    :return:Products which added to cart by user.
    """

    context = AddProductCartService.execute({'product_id': product_id, 'request': request})
    return render(request, 'cart1.html', context)


@login_required
@permission_required('shop.add_cart', raise_exception=True)
def show_product_cart(request):
    """
    Function to show cart items.
    :param request:
    :return:Products which added to cart by user.
    """
    context = ShowProductCartService.execute({'request': request})
    return render(request, 'cart1.html', context)


@login_required
@permission_required('shop.delete_cart', raise_exception=True)
def remove_product_cart(request, product_id):
    """
    Function to remove product from cart.
    :param request:
    :param product_id:
    """
    user = get_user(request)
    context = RemoveProductCartService.execute({'product_id': product_id, 'user': user})
    if context['permission']:
        context['cart_item'].delete()
        return HttpResponseRedirect(reverse('product_cart', args=[0]))
    return HttpResponse('Sorry you dont have permission to delete this object:-{}'.format(product_id))


@login_required
@permission_required('shop.can_checkout', raise_exception=True)
def checkout(request):
    """
    Function to checkout cart products and create delivery object.
    :param request:
    """

    context = CheckoutService.execute({'request': request})
    if type(context['form'].data) == QueryDict:
        return HttpResponseRedirect(reverse('payment_page'))
    return render(request, 'checkout.html', context)


@login_required
@permission_required('shop.view_order', raise_exception=True)
def add_orders(request):
    """
    Function to add order.
    :param request:
    """
    context = AddOrderService.execute({'request': request})
    return render(request, 'orders.html', context)


@login_required
@permission_required('shop.view_order', raise_exception=True)
def show_seller_order(request):
    context = ShowSellerOrderService.execute({'request': request})
    return render(request, 'orders.html', context)


@login_required
@permission_required('shop.delete_order', raise_exception=True)
def delete_orders(request, order_id=None):
    """
    Function to delete order.
    :param order_id:
    :param request:
    """
    context = DeleteOrderService.execute({'order_id': order_id, 'request': request})
    if context['delete'] is None:
        return HttpResponse('Sorry you dont have permission to delete order no.-{}'.format(order_id))
    return HttpResponseRedirect(reverse('show_orders'))


@login_required
def order_detail(request, order_id):
    """
    Function shows the detail of order.
    :param request:
    :param order_id:
    """
    context = OrderDetailService.execute({'request': request, 'order_id': order_id})
    if context['user'] is None:
        return HttpResponse('Sorry you dont have permission to see  order id-{}.'.format(order_id))
    return render(request, 'cart1.html', context)


@login_required
def contact_us(request):
    """
    Function to show contact page.
    :param request:
    :return:
    """
    user = MyUser.objects.get(user_id=request.user.id)
    return render(request, 'contact1.html', {'user': user})


@login_required
@permission_required('shop.can_message', raise_exception=True)
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
