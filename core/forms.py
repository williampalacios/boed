from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

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
                                       required=True)
    shipping_address2 = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'CDMX',
            'type': "text",
            'id': "address-2",
            'class': "form-control"
        }),
                                        required=True)
    shipping_country = CountryField(blank_label='Seleccione País').formfield(
        required=True)
    shipping_zip = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': '09310',
            'type': "text",
            'id': "zip",
            'class': "form-control"
        }),
                                   required=True)
    same_billing_address = forms.BooleanField(required=False)
    save_information = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect,
                                       choices=PAY_CHOICES,
                                       required=True)


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
                                        required=True)
    shipping_country = CountryField(blank_label='Seleccione País').formfield(
        required=True)
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
