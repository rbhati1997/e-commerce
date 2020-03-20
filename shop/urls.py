from django.urls import path, include
from shop import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'cart_item', views.CartItemAViewSet, basename='cart_item')
router.register(r'delivery_address', views.DeliveryAddressModelViewSet, basename='delivery_address')
router.register(r'order_detail', views.OrderDetail, basename='order_detail')


urlpatterns = [
    path('users/', views.UserListDetailView.as_view(), name="users"),
    path('user/<int:user_id>/store/', views.StoreListView.as_view(), name="store"),
    path('user/<int:user_id>/store/<int:store_id>/product/', views.ProductListView.as_view(), name="products"),
    path('product/<int:product_id>/', views.ProductDetailView.as_view(), name="product"),
    path('user/<int:user_id>/cart/', views.CartAPIView.as_view(), name="cart"),
    # path('user/<int:user_id>/cart/<int:cart_id>/cart_item/', views.CartItemAPIView.as_view(), name="cart_item"),
    path('api/', include(router.urls)),
    path('order/', views.OrderList.as_view(), name='order_list'),

    path('api_token_auth/', obtain_auth_token, name='obtain_auth_token'),
    path('rest_auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls'))
]

