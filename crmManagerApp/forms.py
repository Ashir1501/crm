from django import forms
from .models import Customer, Interaction

class CustomerRegisterForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_name','customer_email','customer_phone','customer_company','customer_notes', 'arrived_date','deal_won','deal_assigned']

    customer_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Name'})
    )

    customer_email = forms.EmailField(
        required=True,
        max_length=50,
        widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email Address'})
    )

    customer_phone = forms.CharField(
        required=True,
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Phone Number','pattern':'\d*','min':10})
    )

    customer_company = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Company Name'})
    )

    customer_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class':'form-control'})
    )

    arrived_date = forms.DateField(
        required=True,
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'],
        widget=forms.DateInput(attrs={'type':'date'}),
    )

    deal_won = forms.BooleanField(
        required=False,
        widget=forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')])
    )
