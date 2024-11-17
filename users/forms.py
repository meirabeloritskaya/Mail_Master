from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=False)
    phone_number = forms.CharField(required=False, max_length=15)
    country = forms.CharField(required=False, max_length=50)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "avatar",
            "phone_number",
            "country",
            "password1",
            "password2",
        )
