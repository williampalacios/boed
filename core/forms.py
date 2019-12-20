from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.core.validators import EMPTY_VALUES

PAY_CHOICES = (('E', 'Efectivo'), ('T', 'Transferencia'), ('V',
                                                           'VISA/MASTERCARD'))

SHI_CHOICES = (('P', 'Paquetería'), ('T', 'Recoger en tienda'))


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'Calle sin nómbre, 109',
            'type': "text",
            'id': "address",
            'class': "form-control"
        }),
                                       required=False)
    shipping_address2 = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'CDMX',
            'type': "text",
            'id': "address-2",
            'class': "form-control"
        }),
                                        required=False)
    shipping_country = CountryField(blank_label='Seleccione País').formfield(
        required=False)
    shipping_zip = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': '09310',
            'type': "text",
            'id': "zip",
            'class': "form-control"
        }),
                                   required=False)
    same_billing_address = forms.BooleanField(required=False)
    fact = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={
                'name': "fact",
                'value': "on",
                'type': "checkbox",
                'id': "fact",
                'class': "custom-control-input",
                'onclick': "showHideFact()",
                #'checked': "",
            }),
        required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect,
                                       choices=PAY_CHOICES,
                                       required=True)
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'type': "text",
            'id': "first_name",
            'class': "form-control"
        }),
        required=False)
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'type': "text",
            'id': "last_name",
            'class': "form-control"
        }),
        required=False)
    rfc = forms.CharField(max_length=20,
                          widget=forms.TextInput(attrs={
                              'type': "text",
                              'id': "rfc",
                              'class': "form-control"
                          }),
                          required=False)

    def clean(self):
        fact = self.cleaned_data.get('fact', False)
        if fact:
            shipping_address = self.cleaned_data.get('shipping_address', None)
            shipping_address2 = self.cleaned_data.get('shipping_address2',
                                                      None)
            shipping_country = self.cleaned_data.get('shipping_country', None)
            shipping_zip = self.cleaned_data.get('shipping_zip', None)
            same_billing_address = self.cleaned_data.get(
                'same_billing_address', None)

            payment_option = self.cleaned_data.get('payment_option', None)

            first_name = self.cleaned_data.get('first_name', None)
            last_name = self.cleaned_data.get('last_name', None)
            rfc = self.cleaned_data.get('rfc', None)

            if (shipping_address in EMPTY_VALUES
                ) or (shipping_address2 in EMPTY_VALUES) or (
                    shipping_country in EMPTY_VALUES
                ) or (shipping_zip in EMPTY_VALUES) or (
                    first_name in EMPTY_VALUES) or (
                        last_name in EMPTY_VALUES) or (rfc in EMPTY_VALUES):
                self._errors['shipping_address'] = self.error_class(
                    ['Fact fields missing'])
        return self.cleaned_data


class AddressForm(forms.Form):
    shipping_address = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'Calle sin nómbre, 109',
            'type': "text",
            'id': "address",
            'class': "form-control"
        }),
                                       required=True)
    shipping_address2 = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'CDMX',
            'type': "text",
            'id': "address-2",
            'class': "form-control"
        }),
                                        required=True,
                                        initial='CDMX',
                                        disabled=True)
    shipping_country = CountryField(blank_label='Seleccione País').formfield(
        required=True, initial='MX', disabled=True)
    shipping_zip = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': '09310',
            'type': "text",
            'id': "zip",
            'class': "form-control"
        }),
                                   required=True)


class ShippingOptionsForm(forms.Form):
    shipping_option = forms.ChoiceField(widget=forms.RadioSelect,
                                        choices=SHI_CHOICES,
                                        required=True)


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30,
                                 label='Nombre(s)',
                                 required=True)
    last_name = forms.CharField(max_length=30,
                                label='Apellido(s)',
                                required=True)

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
