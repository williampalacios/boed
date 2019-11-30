from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, View, DetailView
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, Order, OrderItem, Address
from .forms import CheckoutForm
from django.core.paginator import Paginator
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class HomeView(ListView):
    model = Item
    paginate_by = 8
    template_name = "home-page.html"


def HomeViewHerr(request):
    qs_herr = Item.objects.filter(category='H')
    paginator = Paginator(qs_herr, 8)

    page = request.GET.get('page')
    herrts = paginator.get_page(page)
    return render(request, 'home-page-cather.html', {'herrts': herrts})


def HomeViewBic(request):
    qs_herr = Item.objects.filter(category='B')
    paginator = Paginator(qs_herr, 8)

    page = request.GET.get('page')
    herrts = paginator.get_page(page)
    return render(request, 'home-page-catbic.html', {'herrts': herrts})


def HomeViewRef(request):
    qs_herr = Item.objects.filter(category='R')
    paginator = Paginator(qs_herr, 8)

    page = request.GET.get('page')
    herrts = paginator.get_page(page)
    return render(request, 'home-page-catref.html', {'herrts': herrts})


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            qs = Order.objects.filter(user=self.request.user, ordered=False)
            o = qs[0]
            orderItem_qs = OrderItem.objects.filter(order=o)

            total = 0
            for E in orderItem_qs:
                total = total + E.get_total_final_price()

            context = {'object': orderItem_qs, 'total': total}
            return render(self.request, 'order-summary.html', context)
        except:
            messages.info(self.request, "Tu carrito está vacio")
            return redirect('/')


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            qs = Order.objects.filter(user=self.request.user, ordered=False)
            o = qs[0]
            name = self.request.user.first_name + " " + self.request.user.last_name
            address_qs = Address.objects.filter(user=self.request.user)
            a = address_qs[0]
            total = o.total * 100
            key = settings.STRIPE_PUBLISHABLE_KEY
            context = {
                'order': o,
                'name': name,
                'address': a,
                'total': total,
                'key': key
            }
            return render(self.request, 'order-detail-page.html', context)
        except:
            messages.info(self.request, "No tienes pedidos activos")
            return redirect('/')


def charge(request):
    qs = Order.objects.filter(user=request.user, ordered=False)
    o = qs[0]
    amount = round(o.total) * 100
    if request.method == 'POST':
        charge = stripe.Charge.create(amount=amount,
                                      currency='mxn',
                                      description='pago con stripe',
                                      source=request.POST['stripeToken'])
        messages.info(request, "Pago exitoso")
        qs.update(ordered=True, ordered_date=timezone.now(), paid=True)
        return render(request, 'charge.html')


class CheckoutView(View):
    def get(self, *args, **kwargs):

        form = CheckoutForm()
        context = {'form': form}
        return render(self.request, "checkout-page.html", context)

    def post(self, *args, **kwargs):

        try:
            qs = Order.objects.filter(user=self.request.user, ordered=False)
            o = qs[0]  #aquí debe mandar la axcepción...

            form = CheckoutForm(self.request.POST or None)
            print(self.request.POST)
            if form.is_valid():
                shipping_address = form.cleaned_data.get('shipping_address')
                shipping_address2 = form.cleaned_data.get('shipping_address2')
                shipping_country = form.cleaned_data.get('shipping_country')
                shipping_zip = form.cleaned_data.get('shipping_zip')
                #same_billing_address = form.cleaned_data.get('same_billing_address')
                #save_information = form.cleaned_data.get('save_information')
                payment_option = form.cleaned_data.get('payment_option')
                #buscamos la direccion asociada al usurio que envía la orden
                address_qs = Address.objects.filter(user=self.request.user)
                #si existe (solo habrá uno debido a la relación 1-1) lo actualizamos
                if address_qs.exists():
                    address_qs.update(street_address=shipping_address,
                                      city=shipping_address2,
                                      country=shipping_country,
                                      zip=shipping_zip)
                else:  #en otro caso, lo creamos...
                    address = Address(user=self.request.user,
                                      street_address=shipping_address,
                                      city=shipping_address2,
                                      country=shipping_country,
                                      zip=shipping_zip)
                    address.save()
                #buscar Order con usuario request.user y ordered=False (¿Existe la orden?).
                order_qs = Order.objects.filter(user=self.request.user,
                                                ordered=False)
                #si existe, solo debe haber un registro en el qs con ordered=False
                if order_qs.exists():
                    #actualizar el registro
                    order_qs.update(
                        pay_method=payment_option
                    )  #, ordered=True, ordered_date=timezone.now())
                #print(form.cleaned_data)
                #print("the form is valid")
                #messages.info(self.request, "Tu pedido fue realizado con éxito.")

                return redirect('core:order-detail')
            messages.warning(self.request, "Failed checkout")
            return redirect('core:checkout')

        except:
            messages.info(
                self.request,
                "imposible crear la orden... no tienes productos en tu carrito"
            )
            return redirect('/')


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        referer = self.request.META.get('HTTP_REFERER')

        order_qs = []
        if self.request.user.is_authenticated:
            order_qs = Order.objects.filter(user=self.request.user,
                                            ordered=False)

        context['referer'] = referer
        context['request'] = self.request
        context['order_qs'] = order_qs
        return context


@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Item, id=pk)
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
            messages.info(request,
                          "La cantidad de productos ha sido actualizada.")
        else:
            q = OrderItem(item=item, order=order, quantity=1)
            q.save()
            messages.info(request, "El producto se agregó a tu carrito.")
    else:
        ordered_date = timezone.now()
        r = Order(user=request.user, ordered=False)
        r.save()
        oi = OrderItem(item=item, order=r, quantity=1)
        oi.save()
        messages.info(request, "El producto se agregó a tu carrito.")

    #actualizar total de la orden:
    #garantizamos que ya existe la orden... entonces:
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]
    total_act = order.total
    total_aft = total_act + item.get_final_price()
    order_qs.update(total=total_aft)

    return redirect("core:product", pk=pk)


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, id=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    was_there = False
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
            messages.info(request,
                          "La cantidad de productos ha sido actualizada.")
            was_there = True
            #return redirect("core:product", slug=slug)
        else:
            messages.info(request, "Este producto no estaba en tu carrito.")
            #return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Tu carrito está vacio.")
        #return redirect("core:product", slug=slug)
    if order_qs.exists():
        order = order_qs[0]
        order_item = OrderItem.objects.filter(order=order)
        if not order_item.exists():
            order.delete()

    #actualizar total de la orden:
    #si aún existe la orden... entonces:
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists() and was_there:
        order = order_qs[0]
        total_act = order.total
        total_aft = total_act - item.get_final_price()
        order_qs.update(total=total_aft)

    return redirect("core:product", pk=pk)


@login_required
def add_to_cart_os(request, pk):
    item = get_object_or_404(Item, id=pk)
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
            messages.info(request,
                          "La cantidad de productos ha sido actualizada.")
        else:
            q = OrderItem(item=item, order=order, quantity=1)
            q.save()
            messages.info(request, "El producto se agregó a tu carrito.")
    else:
        ordered_date = timezone.now()
        r = Order(user=request.user, ordered_date=ordered_date, ordered=False)
        r.save()
        oi = OrderItem(item=item, order=r, quantity=1)
        oi.save()
        messages.info(request, "El producto se agregó a tu carrito.")

    #actualizar total de la orden:
    #garantizamos que ya existe la orden... entonces:
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]
    total_act = order.total
    total_aft = total_act + item.get_final_price()
    order_qs.update(total=total_aft)

    return redirect("core:order-summary")


@login_required
def remove_from_cart_os(request, pk):
    item = get_object_or_404(Item, id=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    was_there = False
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
            messages.info(request,
                          "La cantidad de productos ha sido actualizada.")
            #return redirect("core:product", slug=slug)
            was_there = True
        else:
            messages.info(request, "Este producto no estaba en tu carrito.")
            #return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Tu carrito está vacio.")
        #return redirect("core:product", slug=slug)
    if order_qs.exists():
        order = order_qs[0]
        order_item = OrderItem.objects.filter(order=order)
        if not order_item.exists():
            order.delete()

    #actualizar total de la orden:
    #si aún existe la orden... entonces:
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists() and was_there:
        order = order_qs[0]
        total_act = order.total
        total_aft = total_act - item.get_final_price()
        order_qs.update(total=total_aft)

    return redirect("core:order-summary")


@login_required
def delete_from_cart_os(request, pk):
    item = get_object_or_404(Item, id=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    quantity = 0
    if order_qs.exists():
        order = order_qs[0]
        order_item = OrderItem.objects.filter(item=item, order=order)
        # si existen... borramos los registros order-item
        if order_item.exists():
            order_item_inst = order_item[0]
            quantity = order_item_inst.quantity
            order_item_inst.delete()
            messages.info(request,
                          "La cantidad de productos ha sido actualizada.")
        else:
            messages.info(request, "Este producto no estaba en tu carrito.")
    else:
        messages.info(request, "Tu carrito está vacio.")
    if order_qs.exists():
        order = order_qs[0]
        order_item = OrderItem.objects.filter(order=order)
        if not order_item.exists():
            order.delete()

    #actualizar total de la orden:
    #si aún existe la orden... entonces:
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        total_act = order.total
        total_aft = total_act - quantity * item.get_final_price()
        order_qs.update(total=total_aft)

    return redirect("core:order-summary")


"""
def CheckoutView(request):
    context = {'items': Item.objects.all()}
    return render(request, "checkout-page.html", context)



def ProductView(request):
    context = {'items': Item.objects.all()}
    return render(request, "product-page.html", context)



class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


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