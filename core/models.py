from django.db import models
from django.conf import settings
from django.shortcuts import reverse, redirect

CATEGORY_CHOICES = (('H', 'Herramientas'), ('R', 'Refacciones'),
                    ('B', 'Bicicletas'))

LABEL_CHOICES = (('P', 'primary'), ('S', 'secondary'), ('D', 'danger'))


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=1)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    image = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", args=[str(self.id)])

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", args=[str(self.id)])

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", args=[str(self.id)])


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.PROTECT)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return "Pedido de: " + str(
            self.order.user) + ", producto: " + self.item.title

    class Meta:
        unique_together = (('item', 'order'))