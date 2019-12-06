from django.urls import path
from .views import HomeView, CheckoutView, ItemDetailView, add_to_cart, remove_from_cart, OrderSummaryView, add_to_cart_os, remove_from_cart_os, delete_from_cart_os, HomeViewHerr, HomeViewBic, HomeViewRef, OrderDetailView, charge, AddressView, ShippingOptionsView, chargeCash

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('home-herr/', HomeViewHerr, name='home-herr'),
    path('home-bic/', HomeViewBic, name='home-bic'),
    path('home-ref/', HomeViewRef, name='home-ref'),
    #path('checkout/', CheckoutView, name='checkout'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('address/', AddressView.as_view(), name='address'),
    path('charge-cash/', chargeCash.as_view(), name='charge-cash'),
    path('shipping-options/',
         ShippingOptionsView.as_view(),
         name='shipping-options'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<pk>/', ItemDetailView.as_view(), name='product'),
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