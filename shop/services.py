from django.shortcuts import get_object_or_404
from service_objects.services import Service
from shop.models import Product, MyUser, Store, CartItem


class DetailStoreViewService(Service):
    def process(self):
        pass


class CreateStoreViewService(Service):
    def process(self):
        user_id = self.data.get('user_id')
        user = get_object_or_404(MyUser, pk=user_id)
        user_store = Store.objects.filter(seller_user_id=user_id)
        if user_store:
            return {"Sorry": "this user already have store."}
        store = Store.objects.create(seller_user=user)
        return store.id


class DetailListProductViewService(Service):

    def process(self):
        # products = Product.objects.all()
        # return products
        pass


class CreateCartItemViewService(Service):
    def process(self):
        product_id = self.data["product"]
        cart_id = self.data["cart"]
        cart_item = CartItem.objects.create(product_id=product_id, cart_id=cart_id)
        return cart_item



