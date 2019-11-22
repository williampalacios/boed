from django.shortcuts import render
from django.views.generic import ListView, View
from .models import Item


def HomeView(request):
    context = {'items': Item.objects.all()}
    return render(request, "home-page.html", context)


def CheckoutView(request):
    context = {'items': Item.objects.all()}
    return render(request, "checkout-page.html", context)


def ProductView(request):
    context = {'items': Item.objects.all()}
    return render(request, "product-page.html", context)


"""
class HomeView(ListView):
    model = Item
    paginated_by = 10
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