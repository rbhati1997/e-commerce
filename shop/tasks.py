from celery import shared_task

from shop.models import OrderSeller


@shared_task
def create_seller_order(order):
    pass
