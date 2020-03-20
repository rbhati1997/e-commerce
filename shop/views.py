from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, mixins, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from shop.models import Product, MyUser, Store, Cart, CartItem, DeliveryAddress, Order
from shop.serializers import ProductSerializer, MyUserSerializer, StoreSerializer, \
    CreateStoreSerializer, ProductUpdateSerializer, CartListSerializer, CartDetailSerializer, \
    CartItemDetailSerializer, DeliveryAddressSerializer, OrderSerializer, OrderUpdateSerializer
from shop.services import CreateStoreViewService, CreateCartItemViewService
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class UserListDetailView(APIView):
    """
    List one and all users.
    """

    def get(self, request, pk=None) -> Response:
        if pk:
            user = MyUser.objects.get(pk=pk)
            serializer = MyUserSerializer(user)
        else:
            users = MyUser.objects.all()
            serializer = MyUserSerializer(users, many=True)

        return Response(serializer.data)

    # def post(self, request):
    #     serializer = MyUserCreateSerializer(data=request.data)
    #     import pdb;pdb.set_trace()
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()


class StoreListView(APIView):
    """
    List of all stores, or create a new store.
    """

    @classmethod
    def get(cls, request, user_id, pk=None) -> Response:
        try:
            # import pdb;pdb.set_trace()
            store = Store.objects.filter(seller_user_id=user_id)
            serializer = StoreSerializer(store, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Store.DoesNotExist:
            return Response({"Error": "Invalid store id {} not exist.".format(pk)})

    @classmethod
    def post(cls, request, user_id) -> Response:
        serializer = CreateStoreSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serial_data = serializer.validated_data
            store = CreateStoreViewService.execute(serial_data)
            if type(store) == int:
                return Response(store.id, status=status.HTTP_201_CREATED)
            return Response(store, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductListView(APIView):
    """
    List all products, or create a new product.
    """
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated,]

    @classmethod
    def get(cls, request, user_id, store_id) -> Response:
        import pdb;pdb.set_trace()
        product_list = Product.objects.filter(store_id=store_id)
        products = cls.paginator.paginate_queryset(product_list, request)
        serializer = ProductSerializer(products, many=True)
        return cls.paginator.get_paginated_response(serializer.data)
        # return Response(serializer.data, status=status.HTTP_200_OK)

    @classmethod
    def post(cls, request, user_id, store_id) -> Response:
        try:
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                product = serializer.save()
                return Response({"Product_id": product.id}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({"Error": "Invalid store id {} not exist.".format(int(request.data["store_id"]))})

        except Exception:
            return Response({"Error": "This ({}) Category does not exist".format(request.data["category"])})


class ProductDetailView(APIView):
    """
    Retrieve, update or delete a product instance.
    """

    @classmethod
    def get_object(cls, pk) -> Product:
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    @classmethod
    def get(cls, request, user_id, store_id, product_id) -> Response:
        product = cls.get_object(product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @classmethod
    def patch(cls, request, product_id) -> Response:
        try:
            product = cls.get_object(product_id)
            serializer = ProductUpdateSerializer(product, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                import pdb;pdb.set_trace()
                return Response(serializer.data, status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Store.DoesNotExist:
            return Response({"Error": "Invalid store id {} not exist.".format(int(request.data["store_id"]))})

    @classmethod
    def delete(cls, request, user_id, store_id, product_id) -> Response:
        product = cls.get_object(product_id)
        product.delete()
        return Response({"Delete: Product successfully deleted."}, status=status.HTTP_204_NO_CONTENT)


class CartAPIView(APIView):
    """
    Create, retrieve, update or delete a cart instance.
    """

    def get(self, request, user_id, pk=None):
        try:
            if pk:
                cart = Cart.objects.get(pk=pk)
                serializer = CartListSerializer(cart)
            else:
                carts = Cart.objects.all()
                serializer = CartListSerializer(carts, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"Error": "Cart for this id-{} doest not exist.".format(pk)}, status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id, ):
        # data = {"data":request.data, "customer_user":request.user}
        serializer = CartDetailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    def delete(self, request, user_id, pk):
        try:
            cart = Cart.objects.get(pk=pk)
            cart.delete()
            return Response({"success": "deleted cart successfully."}, status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({"Error": "Cart for this id-{} doest not exist.".format(pk)}, status.HTTP_404_NOT_FOUND)


class CartItemAViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing, retrieving, deleting or creating Cart items.
    """
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()

    def list(self, request):
        queryset = CartItem.objects.all()
        cart_items = self.paginator.paginate_queryset(queryset, request)
        serializer = CartItemDetailSerializer(cart_items, many=True)
        return self.paginator.get_paginated_response(serializer.data)
        # return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            cart_item = get_object_or_404(CartItem, pk=pk)
            serializer = CartItemDetailSerializer(cart_item)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({"Error": "Cart for this id-{} doest not exist.".format(pk)}, status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = CartItemDetailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            cart_item = CreateCartItemViewService.execute(serializer.data)
            return Response({"cart_item_id": cart_item.id})
        else:
            return Response(serializer.errors)

    def destroy(self, request, pk=None):
        try:
            cart_item = get_object_or_404(CartItem, pk=pk)
            cart_item.delete()
            return Response({"success": "deleted cart item successfully."}, status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({"Error": "Cart item for this id-{} doest not exist.".format(pk)},
                            status.HTTP_404_NOT_FOUND)


class DeliveryAddressModelViewSet(viewsets.ModelViewSet):
    """
    A simple ModelViewSet for viewing, editing, deleting or updating delivery address.
    """
    queryset = DeliveryAddress.objects.all()
    serializer_class = DeliveryAddressSerializer


class OrderList(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    """
    A simple GenericAPIView using mixin to fetch orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class OrderDetail(viewsets.ModelViewSet):
    """
     A viewset that provides the standard actions.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['get'])
    def fetch_order(self, request, pk):
        order = self.get_object()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors)

    @action(detail=True, methods=["patch"])
    def update_order(self, request, pk):
        serializer = OrderUpdateSerializer(self.get_object(), data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"updated": "success for order id-{}".format(pk)}, status.HTTP_200_OK)
        # return Response(serializer.errors)

    @action(detail=True, methods=["delete"])
    def delete_order(self, request, pk):
        order = self.get_object()
        order.delete()
        return Response({"deleted": "success"}, status.HTTP_204_NO_CONTENT)
