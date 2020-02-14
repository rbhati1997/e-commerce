from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from .models import Product, Cart, CustomUser


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
    Function for add product on cart.
    :param request:
    :param product_id:
    :return:Products which added to cart by user.
    """
    user = User.objects.get(pk=request.user.id)
    if product_id > 0:
        product = Product.objects.get(pk=product_id)
        cart_product = Cart.objects.create(customer_user=user)
        cart_product.product.add(product)
    cart_product_list = Product.objects.filter(cart__customer_user_id =user.id)
    return render(request, 'cart1.html', {'cart_product': cart_product_list})


def remove_product_cart(request, product_id):
    """
    Function to remove product from cart.
    :param request:
    :param product_id:
    """
    product = Product.objects.get(pk=product_id)
    product.cart_set.all()[0].delete()
    # pppp = Product.objects.filter(cart__product=product_id).first()
    # import pdb;pdb.set_trace()
    return HttpResponseRedirect(reverse('product_cart', args=[0]))
