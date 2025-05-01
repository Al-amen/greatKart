from django import forms

from .models import CustomUser, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        ),
        label="Password",
    )
    confirm_password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm Password", "class": "form-control"}
        ),
        label="Confirm Password",
    )

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "phone_number"]
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
            "phone_number": forms.TextInput(
                attrs={"placeholder": "Phone Number", "class": "form-control"}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "phone_number")

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        required=False,
        error_messages={"invalid": ("Image files only")},
        widget=forms.FileInput,
    )

    class Meta:
        model = UserProfile
        fields = (
            "address_line_1",
            "address_line_2",
            "division",
            "district",
            "country",
            "profile_picture",
        )

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
