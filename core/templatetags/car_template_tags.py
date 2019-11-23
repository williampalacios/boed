from django import template
from core.models import Order, OrderItem

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        #obtener conteo de items en el carrito
        qs = Order.objects.filter(user=user, ordered=False)
        #obtener el queryset con orden "activa del usuario en sesion"
        if qs.exists():
            o = qs[0]
            cont = 0
            orderItem_qs = OrderItem.objects.filter(order=o)
            #obtener el queryset de "detalles de orden" asociados a la orden
            if orderItem_qs.exists():
                for E in orderItem_qs:
                    #contar el número de artículos por cada instancia del queryset de "detalles de orden"
                    cont = cont + E.quantity
            return cont
    return 0
