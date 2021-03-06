from django.urls import path, re_path
from .views import HomeView, CheckoutView, ItemDetailView, add_to_cart, remove_from_cart, OrderSummaryView, add_to_cart_os, remove_from_cart_os, delete_from_cart_os, HomeViewHerr, HomeViewBic, HomeViewRef, OrderDetailView, charge, AddressView, ShippingOptionsView, chargeCash, PrivacyView, HomeViewAcc, ContactView, OrdersView, OrderView, OrdersViewStaff, UserView, SearchView

app_name = 'core'

urlpatterns = [
    path('orders-staff/', OrdersViewStaff.as_view(), name='orders-staff'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('contact/', ContactView, name='contact'),
    path('', HomeView, name='home'),
    re_path(r'^s/$', SearchView, name='search'),
    path('home-herr/', HomeViewHerr, name='home-herr'),
    path('home-bic/', HomeViewBic, name='home-bic'),
    path('home-ref/', HomeViewRef, name='home-ref'),
    path('home-acc/', HomeViewAcc, name='home-acc'),
    #path('checkout/', CheckoutView, name='checkout'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('address/', AddressView.as_view(), name='address'),
    path('privacy/', PrivacyView.as_view(), name='privacy'),
    path('charge-cash/', chargeCash.as_view(), name='charge-cash'),
    path('shipping-options/',
         ShippingOptionsView.as_view(),
         name='shipping-options'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<pk>/', ItemDetailView.as_view(), name='product'),
    path('order/<pk>/', OrderView.as_view(), name='order'),
    path('user/<pk>', UserView.as_view(), name='user'),
    path('order-detail/', OrderDetailView.as_view(), name='order-detail'),
    path('add-to-cart/<pk>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<pk>', remove_from_cart, name='remove-from-cart'),
    path('add-to-cart-os/<pk>/', add_to_cart_os, name='add-to-cart-os'),
    path('remove-from-cart-os/<pk>',
         remove_from_cart_os,
         name='remove-from-cart-os'),
    path('delete-from-cart-os/<pk>',
         delete_from_cart_os,
         name='delete-from-cart-os'),
    path('charge/', charge, name='charge')  # new
]
"""
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('product/', ProductView.as_view(), name='product')
]
"""