from django.contrib import admin

from .models import Item, OrderItem, Order, Address, Customer, Rfc

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Address)
admin.site.register(Customer)
admin.site.register(Rfc)
