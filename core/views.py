from django.shortcuts import render
from django.views.generic import ListView, View, DetailView
from .models import Item


class HomeView(ListView):
    model = Item
    template_name = "home-page.html"


def CheckoutView(request):
    context = {'items': Item.objects.all()}
    return render(request, "checkout-page.html", context)


def ProductView(request):
    context = {'items': Item.objects.all()}
    return render(request, "product-page.html", context)


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


"""
class HomeView(ListView):
    model = Item
    template_name = "home-page.html"


class CheckoutView(ListView):
    model = Item
    paginate_by = 10
    template_name = "checkout-page.html"


class ProductView(ListView):
    model = Item
    paginate_by = 10
    template_name = "product-page.html"
"""