from django.urls import path
from .views import HomeView, CheckoutView, ProductView, ItemDetailView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView, name='checkout'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product')
]
"""
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('product/', ProductView.as_view(), name='product')
]
"""