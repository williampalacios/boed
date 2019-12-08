from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, View, DetailView
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, Order, OrderItem, Address
from .forms import CheckoutForm, AddressForm, ShippingOptionsForm
from django.core.paginator import Paginator
from django.conf import settings
from django.core.mail import send_mail
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class PrivacyView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'privacy.html')


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


class ShippingOptionsView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = ShippingOptionsForm()
        context = {'form': form}
        return render(self.request, "shipping-options.html", context)

    def post(self, *args, **kwargs):
        try:
            qs = Order.objects.filter(user=self.request.user, ordered=False)
            o = qs[0]  #aquí debe mandar la axcepción...

            form = ShippingOptionsForm(self.request.POST or None)
            if form.is_valid():
                shipping_option = form.cleaned_data.get('shipping_option')

                #buscamos la direccion de facturación asociada al usurio que envía la orden
                address_qs = Address.objects.filter(user=self.request.user,
                                                    main=True)

                #si no la tiene, lo mandamos a crear una...
                if not address_qs.exists():
                    messages.info(
                        self.request,
                        "Aún no tenemos tu información de facturación, por favor llena el formulario"
                    )
                    return redirect('core:checkout')
                else:  #actualizamos el método de envío en su orden
                    o = qs[0]
                    was_p = o.shipping_option == 'P'
                    qs.update(shipping_option=shipping_option)
                    if shipping_option == 'P':
                        if not was_p:
                            qs.update(total=o.total + 50)
                        return redirect('core:address')
                    else:
                        if was_p:
                            qs.update(total=o.total - 50)
                        return redirect('core:order-detail')
            else:
                messages.warning(self.request,
                                 "Falló el formulario shipping_options")
                return redirect('core:shipping-options')
        except:
            messages.info(
                self.request,
                "imposible crear la orden... no tienes productos en tu carrito"
            )
            return redirect('/')


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            qs = Order.objects.filter(user=self.request.user, ordered=False)
            o = qs[0]
            name = self.request.user.first_name + " " + self.request.user.last_name
            address_qs = Address.objects.filter(user=self.request.user,
                                                main=True)
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
    try:
        o = qs[0]
    except:
        messages.info(
            request,
            "No se pudo completar la compra, NO se realizó ningún cargo a su tarjeta"
        )
        return redirect('/')
    amount = round(o.total) * 100
    if request.method == 'POST':
        charge = stripe.Charge.create(amount=amount,
                                      currency='mxn',
                                      description='pago con stripe',
                                      source=request.POST['stripeToken'])
        messages.info(request, "Pago exitoso")
        qs.update(ordered=True, ordered_date=timezone.now(), paid=True)

        #Mailing
        message = "¡Gracias por su compra!\nDetalles del pedido NUM. " + str(
            o.id) + "\n"
        orderItem_qs = OrderItem.objects.filter(order=o)
        prodStr = ""
        for E in orderItem_qs:
            prodStr = prodStr + str(E.item) + " | " + str(
                E.quantity) + " | $" + str(E.get_total_final_price()) + "\n"
        message = message + prodStr
        if o.shipping_option == 'P':
            message = message + "Costo de envío: $50\n"
        message = message + "Total: $" + str(o.total)
        message = message + "\nPagado con VISA/MASTERCARD"
        message = message + "\nMétodo de envío: "
        if o.shipping_option == 'P':
            message = message + "Paquetería, se ennviará a: " + o.address.street_address + " en un plazo máximo de 48 horas.\n\n¡Es un placer atenderle!\nSoporte: " + settings.EMAIL_HOST_USER + ", 5526774403"
        else:
            message = message + "Recolección en tienda " + "(11 de Agosto de 1859,109 Iztapalapa Ciudad de México C.P. 09310) Teléfono: 5526774403"
            message = message + "\nPuede recoger su pedido pasadas 24 horas de haber recibido este correo"
            message = message + "\n\n¡Es un placer atenderle!\nSoporte: " + settings.EMAIL_HOST_USER + ", 5526774403"
        send_mail(
            'Resumen de su compra en www.bicicletasonce.com.mx',
            message,
            settings.EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=False,
        )

        context = {'email': request.user.email}
        return render(request, 'charge.html', context)


class chargeCash(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        qs = Order.objects.filter(user=self.request.user, ordered=False)
        try:
            o = qs[0]
        except:
            messages.info(self.request, "No se pudo completar la compra")
            return redirect('/')
        qs.update(ordered=True, ordered_date=timezone.now())

        #Mailing
        message = "¡Gracias por su compra!\nDetalles del pedido NUM. " + str(
            o.id) + "\n"
        orderItem_qs = OrderItem.objects.filter(order=o)
        prodStr = ""
        for E in orderItem_qs:
            prodStr = prodStr + E.item.title + " | " + str(
                E.quantity) + " | $" + str(E.get_total_final_price()) + "\n"
        message = message + prodStr
        if o.shipping_option == 'P':
            message = message + "Costo de envío: $50\n"
        message = message + "Total: $" + str(o.total)
        if o.pay_method == 'E':
            message = message + "\nA pagar en efectivo."
        else:
            message = message + "\nA pagar por transferencia/depósito."
        message = message + "\nMétodo de envío: "
        if o.shipping_option == 'P':
            message = message + "Paquetería, una vez validado el pago, se ennviará a: " + o.address.street_address
            message = message + "\nDebe enviar un mensaje por WhatsApp con el COMPROBANTE DE PAGO y NUM. DE PEDIDO al 5526774403 EN UN PLAZO NO MAYOR A 24 HORAS despues de su compra."
            message = message + "\n\nDatos para el depósito:\nCuenta de HSBC: 4213 1660 7646 5891\nTipo de cuenta: Débito\nConcepto de pago: bicicletasonce pedido " + str(
                o.id)
            message = message + "\nEn caso de NO ENVIAR SU COMPRABANTE en un plazo de 24 horas despues de recibido este correo, su pedido será cancelado."
            message = message + "\n\n¡Es un placer atenderle!\nSoporte: " + settings.EMAIL_HOST_USER + ", 5526774403"
        else:
            if o.pay_method == "E":
                message = message + "Recolección en tienda " + "(11 de Agosto de 1859,109 Iztapalapa Ciudad de México C.P. 09310) Teléfono: 5526774403"
                message = message + "\nPor favor le pedimos que confirme su pedido mandando un mensaje con su NUM. DE PEDIDO por WhatsApp al 5526774403. Una vez que confirme, el equipo de Bicicletas Once preparará sus productos para ser entregados."
                message = message + "\nPuede recoger su pedido pasadas 24 horas de su confirmación por WhatsApp"
                message = message + "\nEn caso de NO CONFIRMAR en un plazo de 24 horas despues de recibido este correo, su pedido será cancelado."
                message = message + "\n\n¡Es un placer atenderle!\nSoporte: " + settings.EMAIL_HOST_USER + ", 5526774403"
            else:
                message = message + "Recolección en tienda " + "(11 de Agosto de 1859,109 Iztapalapa Ciudad de México C.P. 09310) Teléfono: 5526774403"
                message = message + "\nDebe enviar un mensaje por WhatsApp con el COMPROBANTE DE PAGO y NUM. DE PEDIDO al 5526774403 EN UN PLAZO NO MAYOR A 24 HORAS despues de su compra."
                message = message + "\n\nDatos para el depósito:\nCuenta de HSBC: 4213 1660 7646 5891\nTipo de cuenta: Débito\nConcepto de pago: bicicletasonce pedido " + str(
                    o.id)
                message = message + "\nPuede recoger su pedido pasadas 24 horas de haber enviado su comprabante"
                message = message + "\nEn caso de NO ENVIAR SU COMPRABANTE en un plazo de 24 horas despues de recibido este correo, su pedido será cancelado."
                message = message + "\n\n¡Es un placer atenderle!\nSoporte: " + settings.EMAIL_HOST_USER + ", 5526774403"
        send_mail(
            'Resumen de su compra en www.bicicletasonce.com.mx',
            message,
            settings.EMAIL_HOST_USER,
            [self.request.user.email],
            fail_silently=False,
        )
        context = {'email': self.request.user.email}
        return render(self.request, "charge.html", context)


class AddressView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = AddressForm()
        address_qs = Address.objects.filter(user=self.request.user, main=False)
        if address_qs.exists():
            a = address_qs[0]
            form.fields['shipping_address'].initial = a.street_address
            form.fields['shipping_address2'].initial = a.city
            form.fields['shipping_country'].initial = a.country
            form.fields['shipping_zip'].initial = a.zip
        context = {'form': form}
        return render(self.request, "address-page.html", context)

    def post(self, *args, **kwargs):
        try:
            qs = Order.objects.filter(user=self.request.user, ordered=False)
            o = qs[0]  #aquí debe mandar la axcepción...

            form = AddressForm(self.request.POST or None)
            if form.is_valid():
                shipping_address = form.cleaned_data.get('shipping_address')
                shipping_address2 = form.cleaned_data.get('shipping_address2')
                shipping_country = form.cleaned_data.get('shipping_country')
                shipping_zip = form.cleaned_data.get('shipping_zip')

                order_qs = Order.objects.filter(user=self.request.user,
                                                ordered=False)
                #buscamos la direccion de envío asociada al usurio que envía la orden y su dirección de facturación
                address_qs_sc = Address.objects.filter(user=self.request.user,
                                                       main=False)
                address_qs = Address.objects.filter(user=self.request.user,
                                                    main=True)

                #si existe la direccion de envío asociada (solo habrá uno debido "unique together"), lo actualizamos
                if address_qs_sc.exists():
                    address_qs_sc.update(street_address=shipping_address,
                                         city=shipping_address2,
                                         country=shipping_country,
                                         zip=shipping_zip)
                    address_sc = address_qs_sc[0]
                    order_qs.update(address=address_sc)
                    #si tiene dirección de facturación:
                    if address_qs.exists():
                        return redirect('core:order-detail')
                    else:
                        messages.info(
                            self.request,
                            "Aún no tenemos tu información de facturación, por favor llena el formulario"
                        )
                        return redirect('core:checkout')
                else:  #la creamos
                    address_sc = Address(user=self.request.user,
                                         street_address=shipping_address,
                                         city=shipping_address2,
                                         country=shipping_country,
                                         zip=shipping_zip,
                                         main=False)
                    address_sc.save()
                    order_qs.update(address=address_sc)
                    #si tiene dirección de facturación:
                    if address_qs.exists():
                        return redirect('core:order-detail')
                    else:
                        messages.info(
                            self.request,
                            "Aún no tenemos tu información de facturación, por favor llena el formulario"
                        )
                        return redirect('core:checkout')
            else:
                messages.warning(self.request, "Falló el formulario address")
                return redirect('core:address')
        except:
            messages.info(
                self.request,
                "imposible crear la orden... no tienes productos en tu carrito"
            )
            return redirect('/')


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        address_qs = Address.objects.filter(user=self.request.user, main=True)
        if address_qs.exists():
            a = address_qs[0]
            form.fields['shipping_address'].initial = a.street_address
            form.fields['shipping_address2'].initial = a.city
            form.fields['shipping_country'].initial = a.country
            form.fields['shipping_zip'].initial = a.zip
        context = {'form': form}
        return render(self.request, "checkout-page.html", context)

    def post(self, *args, **kwargs):

        qs = Order.objects.filter(user=self.request.user, ordered=False)
        try:
            o = qs[0]  #aquí debe mandar la axcepción...
        except:
            messages.info(
                self.request,
                "imposible crear la orden... no tienes productos en tu carrito"
            )
            return redirect('/')

        form = CheckoutForm(self.request.POST or None)
        print(self.request.POST)
        if form.is_valid():
            shipping_address = form.cleaned_data.get('shipping_address')
            shipping_address2 = form.cleaned_data.get('shipping_address2')
            shipping_country = form.cleaned_data.get('shipping_country')
            shipping_zip = form.cleaned_data.get('shipping_zip')
            same_billing_address = form.cleaned_data.get(
                'same_billing_address')
            #save_information = form.cleaned_data.get('save_information')
            payment_option = form.cleaned_data.get('payment_option')

            #buscamos la direccion principal asociada al usurio que envía la orden
            address_qs = Address.objects.filter(user=self.request.user,
                                                main=True)
            #si existe (solo habrá uno debido "unique together") lo actualizamos
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
                                  zip=shipping_zip,
                                  main=True)
                address.save()

            order_qs = Order.objects.filter(user=self.request.user,
                                            ordered=False)
            if same_billing_address:
                #buscamos la direccion de envío asociada al usurio que envía la orden
                address_qs_sc = Address.objects.filter(user=self.request.user,
                                                       main=False)
                #si existe (solo habrá uno debido "unique together"), lo actualizamos
                if address_qs_sc.exists():
                    address_qs_sc.update(street_address=shipping_address,
                                         city=shipping_address2,
                                         country=shipping_country,
                                         zip=shipping_zip)
                    address_sc = address_qs_sc[0]
                    order_qs.update(pay_method=payment_option,
                                    address=address_sc)
                else:
                    address_sc = Address(user=self.request.user,
                                         street_address=shipping_address,
                                         city=shipping_address2,
                                         country=shipping_country,
                                         zip=shipping_zip,
                                         main=False)
                    address_sc.save()
                    order_qs.update(pay_method=payment_option,
                                    address=address_sc)
            else:
                order_qs.update(pay_method=payment_option)
            if not payment_option == 'E':
                return redirect('core:shipping-options')
            else:
                was_p = o.shipping_option == 'P'
                qs.update(shipping_option='T')
                if was_p:
                    qs.update(total=o.total - 50)
                return redirect('core:order-detail')

            #print(form.cleaned_data)
            #print("the form is valid")
        else:
            messages.warning(self.request, "Falló el formulario checkout")
            return redirect('core:checkout')


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