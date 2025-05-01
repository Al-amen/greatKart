from django import forms

from .models import Order


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "address_line_1",
            "address_line_2",
            "country",
            "division",
            "district",
            "order_note",
        )
        widgets = {
            "first_name": forms.TextInput(
                attrs={"placeholder": "First Name", "class": "form-control"}
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "Last Name", "class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "Email", "class": "form-control"}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "Phone Number", "class": "form-control"}
            ),
            "address_line_1": forms.TextInput(
                attrs={"placeholder": "address_line_1", "class": "form-control"}
            ),
            "address_line_2": forms.TextInput(
                attrs={"placeholder": "address_line_2", "class": "form-control"}
            ),
            "country": forms.EmailInput(
                attrs={"placeholder": "country", "class": "form-control"}
            ),
            "division": forms.TextInput(
                attrs={"placeholder": "division", "class": "form-control"}
            ),
            "district": forms.EmailInput(
                attrs={"placeholder": "district", "class": "form-control"}
            ),
            "order_note": forms.TextInput(
                attrs={"placeholder": "order_note", "class": "form-control"}
            ),
        }
