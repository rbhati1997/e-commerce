from shop.models import Order, Product, CartItem, MyUser
from django.db.models import Q
from itertools import chain


def get_user(request):
    """
    Function to fetch current user.
    :return:
    """
    return MyUser.objects.get(pk=request.user.id)


def seller_ordered_products(user):
    """
    Function shows the ordered products to the seller.
    :param user:
    :return: Orders.
    """
    orders_list = []

    for order in Order.objects.all():
        for product in order.product.all():
            if user == product.store.seller_user:
                orders_list.append(order)

    return set(orders_list)


def global_search_bar(request):
    """
    Function to search term of search-bar.
    :param request:
    :return:search terms.
    """
    search_term = request['search']
    product = Product.objects.filter(
        Q(name__icontains=search_term) | Q(category__icontains=search_term) | Q(description__icontains=search_term))
    cart_item = CartItem.objects.filter(
        Q(product__name__icontains=search_term) | Q(product__category__icontains=search_term) | Q(
            product__description__icontains=search_term))
    return chain(cart_item, product)


def total_price(products):
    """
    Function to calculate total price of products.
    :param products:
    :return: Total price.
    """
    price = 0
    for cart_product in products:
        price += int(cart_product.product.price)
    return price
