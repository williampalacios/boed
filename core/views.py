from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View, DetailView
from django.utils import timezone
from django.contrib import messages
from .models import Item, Order, OrderItem


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


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    #buscar Order con usuario request.user y ordered=False (¿Existe la orden?).
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        order_item = OrderItem.objects.filter(item=item, order=order)
        # revisar si el item está en la orden
        if order_item.exists():
            order_item_inst = order_item[0]
            order_item_inst.quantity += 1
            order_item_inst.save()
            messages.info(request, "This item quantity was updated.")
        else:
            q = OrderItem(item=item, order=order, quantity=1)
            q.save()
            messages.info(request, "This item was added to your cart.")
    else:
        ordered_date = timezone.now()
        r = Order(user=request.user, ordered_date=ordered_date, ordered=False)
        r.save()
        oi = OrderItem(item=item, order=r, quantity=1)
        oi.save()
        messages.info(request, "This item was added to your cart.")
    return redirect("core:product", slug=slug)


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        order_item = OrderItem.objects.filter(item=item, order=order)
        # check if the order item is in the order
        if order_item.exists():
            order_item_inst = order_item[0]
            order_item_inst.quantity -= 1
            order_item_inst.save()
            if order_item_inst.quantity == 0:
                order_item_inst.delete()
            messages.info(request, "This item was removed from your cart.")
            #return redirect("core:product", slug=slug)
        else:
            messages.info(request, "This item was not in your cart")
            #return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        #return redirect("core:product", slug=slug)
    if order_qs.exists():
        order = order_qs[0]
        order_item = OrderItem.objects.filter(order=order)
        if not order_item.exists():
            order.delete()
    return redirect("core:product", slug=slug)


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