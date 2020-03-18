from rest_framework import serializers

from shop.models import Product, MyUser, Store, Cart, CartItem, DeliveryAddress, Order


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ["id", "username", "user_type"]


# class MyUserCreateSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(max_length=100,required=True)
#     email = serializers.EmailField(required=False)
#     password1 = serializers.CharField(max_length=10, required=True)
#     password2 = serializers.CharField(max_length=10, required=True)
#
#     class Meta:
#         model = MyUser
#         fields = ["id"]
#
#     def create(self, validated_data):
#         import pdb;pdb.set_trace()
#         pass


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class CreateStoreSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Store
        fields = ["user_id"]


class ProductSerializer(serializers.ModelSerializer):
    """
    Product Serializer for get and post method.
    """
    image = serializers.ImageField(required=False)
    store_id = serializers.IntegerField(required=True)

    class Meta:
        model = Product
        exclude = ["store"]

    def create(self, validated_data):
        return Product.objects.create(**validated_data)


class ProductUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    store_id = serializers.IntegerField(required=False)

    class Meta:
        model = Product
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.category = validated_data.get('category', instance.category)
        instance.price = validated_data.get('price', instance.price)
        instance.description = validated_data.get('description', instance.description)
        instance.name = validated_data.get('name', instance.name)
        instance.available = validated_data.get('available', instance.available)
        instance.store_id = validated_data.get('store_id', instance.store_id)
        instance.save()
        return instance


class CartListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"


class CartDetailSerializer(serializers.ModelSerializer):
    customer_user = serializers.IntegerField(required=True)

    class Meta:
        model = Cart
        fields = "__all__"

    def create(self, validated_data):
        pass


class CartItemDetailSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(default=1)
    cart_id = serializers.IntegerField(required=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'cart_id', 'quantity']


class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    # product = ProductSerializer(many=True, read_only=True, source="product_order")

    class Meta:
        model = Order
        fields = "__all__"

    def create(self, validated_data):
        products = validated_data.pop("product")
        Order1 = Order.objects.create(**validated_data)
        for product in products:
            Order1.product.add(product)
        return Order1


class OrderUpdateSerializer(serializers.ModelSerializer):
    customer_user = serializers.IntegerField(required=False)

    class Meta:
        model = Order
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.delivery_address_id = validated_data.get('delivery_address', instance.delivery_address)
        instance.customer_user_id = validated_data.get('customer_user', instance.customer_user)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        products = validated_data.get('product', instance.product)
        for product in products:
            instance.product.add(product)
        instance.save()
        return instance
