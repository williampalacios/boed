from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAY_CHOICES = (('E', 'Efectivo'), ('T', 'Transferencia'))


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': '1234 Main St',
            'type': "text",
            'id': "address",
            'class': "form-control"
        }),
                                       required=True)
    shipping_address2 = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'Interior',
            'type': "text",
            'id': "address-2",
            'class': "form-control"
        }),
                                        required=True)
    shipping_country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={
            'class': "custom-select d-block w-100",
            'id': "country"
        }),
        required=True)
    shipping_zip = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'Zip',
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


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='Nombre(s)')
    last_name = forms.CharField(max_length=30, label='Apellido(s)')

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
