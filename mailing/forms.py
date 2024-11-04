from django import forms
from .models import Client, Message, Newsletter


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["email", "full_name", "comment"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body"]


class NewsletterForm(forms.ModelForm):
    sent_date = forms.DateTimeField(
        input_formats=["%Y-%m-%d %H:%M"],
        widget=forms.DateTimeInput(
            attrs={"placeholder": "ГГГГ-ММ-ДД ЧЧ:ММ", "class": "form-control"}
        ),
        required=False,
    )

    end_date = forms.DateTimeField(
        input_formats=["%Y-%m-%d %H:%M"],
        widget=forms.DateTimeInput(
            attrs={"placeholder": "ГГГГ-ММ-ДД ЧЧ:ММ", "class": "form-control"}
        ),
        required=False,
    )

    class Meta:
        model = Newsletter
        fields = ["sent_date", "end_date", "messages", "recipients"]
        widgets = {
            "recipients": forms.CheckboxSelectMultiple(),
            "messages": forms.CheckboxSelectMultiple(),
        }
