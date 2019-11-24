from django.urls import path
from .views import HomeView, CheckoutView, ProductView, ItemDetailView, add_to_cart, remove_from_cart, OrderSummaryView, add_to_cart_os, remove_from_cart_os, delete_from_cart_os

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView, name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<pk>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<pk>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<pk>', remove_from_cart, name='remove-from-cart'),
    path('add-to-cart-os/<pk>/', add_to_cart_os, name='add-to-cart-os'),
    path('remove-from-cart-os/<pk>',
         remove_from_cart_os,
         name='remove-from-cart-os'),
    path('delete-from-cart-os/<pk>',
         delete_from_cart_os,
         name='delete-from-cart-os')
]
"""
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('product/', ProductView.as_view(), name='product')
]
"""