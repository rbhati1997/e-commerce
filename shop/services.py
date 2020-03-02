from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from service_objects.services import Service
from shop.forms import DeliveryAddressForm, ProductForm
from shop.models import Product, Cart, CartItem, DeliveryAddress, Order, Store
from shop.utils import global_search_bar, get_user, total_price, seller_ordered_products


class ProductGridService(Service):
    """
    Service function which consist business logic of product_grid view.
    :return Context.
    """

    def process(self):
        user = self.data['user']
        get_request = self.data['get_request']
        # When user is customer.
        if user.is_customer:
            product_list = Product.objects.all()
            if 'search' in get_request:
                product_list = global_search_bar(get_request)
            paginator1 = Paginator(product_list, 3)
            page_number = get_request.get('page')
            if page_number:
                products = paginator1.get_page(page_number)
            else:
                products = paginator1.get_page(1)

        # When user is seller.
        elif user.is_seller:
            products = Product.objects.filter(store__seller_user=user)

        return {
            "user": user,
            'products': products,
            'grid_view': 'grid_view'
        }


class ProductDetailService(Service):
    """
    Service function which consist business logic of product_detail view.
    :return Context.
    """

    def process(self):
        user = get_user(self.data['request'])
        product = get_object_or_404(Product, pk=self.data['pk'])
        return {
            'product': product,
            'user': user,
            'permission': user.has_perm('view_product', product)
        }


class AddProductCartService(Service):
    """
    Service function which consist business logic of add_product_cart view.
    :return Context.
    """

    def process(self):
        request = self.data['request']
        user = get_user(request)

        cart = Cart.objects.get_or_create(customer_user=user)
        cart_item = CartItem(product_id=self.data['product_id'], cart=cart[0])
        cart_item.save(request=request)

        cart_items = CartItem.objects.filter(cart__customer_user=user)
        price = total_price(cart_items)

        return {
            "cart_product": cart_items,
            "cart_products_price": price,
            'user': user
        }


class ShowProductCartService(Service):
    """
    Service function which consist business logic of show_product_cart view.
    :return Context.
    """

    def process(self):
        user = get_user(self.data['request'])
        cart_items = CartItem.objects.filter(cart__customer_user=user)
        price = total_price(cart_items)

        return {
            "cart_product": cart_items,
            "cart_products_price": price,
            'user': user
        }


class RemoveProductCartService(Service):
    """
    Service function which consist business logic of remove_product_cart view.
    :return Context.
    """

    def process(self):
        cart_item = CartItem.objects.get(pk=self.data['product_id'])
        permission = self.data['user'].has_perm('delete_cartitem', cart_item)
        return {'permission': permission, 'cart_item': cart_item}


class DeleteProductService(Service):
    """
    Service function which consist business logic of delete_product view.
    :return Context.
    """

    def process(self):
        product = Product.objects.get(pk=self.data['product_id'])
        permission = self.data['user'].has_perm('delete_product', product)
        return {'permission': permission, 'product': product}


class AddProductService(Service):
    """
    Service function which consist business logic of delete_product view.
    :return Context.
    """

    def process(self):
        request = self.data['request']
        user = get_user(request)
        store = Store.objects.get_or_create(seller_user=user)
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save(request)
                return {"form": form, 'user': False}

        form = ProductForm(initial={'store': store})
        return {'form': form, 'user': user}


class CheckoutService(Service):
    """
    Service function which consist business logic of checkout view.
    :return Context.
    """

    def process(self):
        request = self.data['request']
        user = get_user(request)
        if request.method == "POST":
            form = DeliveryAddressForm(request.POST)
            if form.is_valid():
                delivery_address = form.save()
            request.session['delivery_address_id'] = delivery_address.id
            return {'form': form}
        cart_product_list = CartItem.objects.all()
        price = total_price(cart_product_list)
        form = DeliveryAddressForm(initial={'customer_user': user})
        context = {
            "cart_product": cart_product_list,
            "cart_products_price": price,
            "form": form,
            'user': user
        }
        return context


class AddOrderService(Service):
    """
    Service function which consist business logic of add_order view.
    :return Context.
    """

    def process(self):
        request = self.data['request']
        user = get_user(request)

        cart_items = CartItem.objects.filter(cart__customer_user=user)
        delivery_address = DeliveryAddress.objects.filter(pk=request.session.get('delivery_address_id'))
        order = Order(customer_user=user, delivery_address=delivery_address[0])
        order.save(request=request)
        for cart_item in cart_items:
            order.product.add(cart_item.product)
            order.save(request=request)
            cart_item.delete()

        return {
            'user': user,
            'order': Order.objects.filter(customer_user=user)
        }


class ShowSellerOrderService(Service):
    """
    Service function which consist business logic of show_seller_order view.
    :return Context.
    """

    def process(self):
        request = self.data['request']
        user = get_user(request)
        if user.is_seller:
            return {
                'user': user,
                'order': seller_ordered_products(user)
            }
        return {
            'user': user,
            'order': Order.objects.filter(customer_user=user)
        }


class DeleteOrderService(Service):
    """
    Service function which consist business logic of delete_order view.
    :return dict.
    """

    def process(self):
        request = self.data['request']
        user = get_user(request)
        order = Order.objects.get(pk=self.data['order_id'])
        if not user.has_perm('delete_order', order):
            return {'delete':None}
        order.delete()
        return {'delete': 'deleted successfully'}


class OrderDetailService(Service):
    """
    Service function which consist business logic of order_detail view.
    :return Context.
    """

    def process(self):
        order_id = self.data['order_id']
        request = self.data['request']
        user = get_user(request)
        price = 0
        order = Order.objects.get(pk=order_id)
        products = order.product.all()
        if not user.has_perm('view_order', order):
            return {"user": None}
        product_list = []
        for product in products:
            if user.is_customer:
                product_list.append(product)
            elif user == product.store.seller_user:
                product_list.append(product)

        for cart_product in product_list:
            price += int(cart_product.price)

        return {
            "cart_product": product_list,
            "cart_products_price": price,
            "order_detail": "order detail",
            "user": user
        }
