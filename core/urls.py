from django.urls import path
from .views import HomeView, CheckoutView, ProductView

app_name = 'core'

urlpatterns = [
    path('', HomeView, name='home'),
    path('checkout/', CheckoutView, name='checkout'),
    path('product/', ProductView, name='product')
]
"""
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('product/', ProductView.as_view(), name='product')
]
"""