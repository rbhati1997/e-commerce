from django.core.paginator import Paginator
from service_objects.services import Service
from shop.forms import DeliveryAddressForm
from shop.models import Product, Cart, CartItem, DeliveryAddress, Order
from shop.utils import global_search_bar, get_user, total_price, seller_ordered_products


class ProductGridService(Service):
    """
    Service function which consist business logic of product_grid view.
    :return Context.
    """

    def process(self):
        user = self.data['user']
        get_request = self.data['get_request']
        # When user type is customer.
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
        # When user type is seller.
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
        pk = self.data['pk']
        user = get_user(self.data['request'])
        product = Product.objects.get(pk=pk)
        return {
            'product': product,
            'user': user
        }


class AddProductCartService(Service):
    """
    Service function which consist business logic of add_product_cart view.
    :return Context.
    """

    def process(self):
        product_id = self.data['product_id']
        request = self.data['request']
        user = get_user(request)
        if product_id > 0:
            product = Product.objects.get(pk=product_id)
            cart = Cart.objects.get_or_create(customer_user=user)
            CartItem.objects.create(product=product, cart=cart[0])

        cart_items = CartItem.objects.all()
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
        product_id = self.data['product_id']
        CartItem.objects.get(pk=product_id).delete()
        return {'deleted': 'deleted successfully'}


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
        order_id = self.data['order_id']
        request = self.data['request']
        user = get_user(request)
        # When user is customer.
        if user.is_customer:
            cart_items = CartItem.objects.filter(cart__customer_user=user)
            delivery_address = DeliveryAddress.objects.filter(pk=request.session.get('delivery_address_id'))

            if not order_id:
                order = Order.objects.create(customer_user=user, delivery_address=delivery_address[0])
                for cart_item in cart_items:
                    order.product.add(cart_item.product)
                    order.save()
                    cart_item.delete()
            return {
                'user': user,
                'order': Order.objects.all()
            }

        # When user is seller.
        elif user.is_seller:
            return {
                'user': user,
                'order': seller_ordered_products(user)
            }


class DeleteOrderService(Service):
    """
    Service function which consist business logic of delete_order view.
    :return dict.
    """

    def process(self):
        order_id = self.data['order_id']
        if order_id:
            order = Order.objects.get(pk=order_id)
            order.delete()
        else:
            Order.objects.all().delete()

        return{'delete': 'deleted successfully'}


class OrderDetailService(Service):
    """
    Service function which consist business logic of order_detail view.
    :return Context.
    """

    def process(self):
        pass