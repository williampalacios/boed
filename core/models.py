from django.db import models
from django.conf import settings
from django.shortcuts import reverse, redirect
from django_countries.fields import CountryField

CATEGORY_CHOICES = (('H', 'Herramientas'), ('R', 'Refacciones'),
                    ('B', 'Bicicletas'), ('A', 'Accesorios'))

LABEL_CHOICES = (('P', 'primary'), ('S', 'secondary'), ('D', 'danger'))

PAY_CHOICES = (('E', 'Efectivo'), ('T', 'Transferencia'), ('V',
                                                           'VISA/MASTERCARD'))

SHI_CHOICES = (('P', 'paquetería'), ('T', 'tienda'))


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=1)
    #label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    image = models.ImageField(upload_to='img', null=True, blank=True)
    description = models.TextField()
    stock = models.IntegerField(default=-1)
    prov = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", args=[str(self.id)])

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", args=[str(self.id)])

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", args=[str(self.id)])

    def get_add_to_cart_url_os(self):
        return reverse("core:add-to-cart-os", args=[str(self.id)])

    def get_remove_from_cart_url_os(self):
        return reverse("core:remove-from-cart-os", args=[str(self.id)])

    def get_delete_from_cart_url_os(self):
        return reverse("core:delete-from-cart-os", args=[str(self.id)])

    def get_final_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price

    def on_stock(self):
        if self.stock != 0:
            return True
        return False


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=100, blank=True, null=True)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100, null=False)
    city = models.CharField(max_length=100, null=False)
    country = CountryField(multiple=False, null=False)
    zip = models.CharField(max_length=10, null=False)
    main = models.BooleanField(default=False)

    def __str__(self):
        return self.street_address + " | " + self.city + " | " + str(
            self.country
        ) + " | " + self.zip + " | " + self.user.first_name + " | " + str(
            self.main)

    class Meta:
        unique_together = (('user', 'main'))


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.PROTECT)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(null=True, blank=True)
    ordered = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    pay_method = models.CharField(choices=PAY_CHOICES,
                                  max_length=1,
                                  null=True,
                                  blank=True)
    total = models.FloatField(default=0)
    same_billing_address = models.BooleanField(default=False)
    fact = models.BooleanField(default=False)
    address = models.ForeignKey(Address,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True)
    shipping_option = models.CharField(choices=SHI_CHOICES,
                                       max_length=1,
                                       null=True,
                                       blank=True)

    def __str__(self):
        return "pedido " + str(
            self.id) + " de " + self.user.first_name + " ¿Ordenado?: " + str(
                self.ordered)

    def get_absolute_url(self):
        return reverse("core:order-detail", args=[str(self.id)])


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return "Pedido: " + str(
            self.order.id) + ", producto: " + self.item.title

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return (self.item.price - self.item.discount_price) * self.quantity

    def get_total_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    class Meta:
        unique_together = (('item', 'order'))