from shop.models import Order


def seller_ordered_products(user):
    """
    Function shows the ordered products to the seller.
    :param user:
    :return: Orders.
    """
    orders = []
    for order in Order.objects.all():
        for product in order.product.all():
            if user == product.store.seller_user:
                orders.append(product)
    return orders

