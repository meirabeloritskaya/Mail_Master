from django.contrib import admin
from .models import Client, Message, Newsletter, DeliveryAttempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "comment", "owner")
    search_fields = ("email", "full_name", "owner")
    permissions = ["can_view_client"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "is_sent", "client", "owner")
    list_filter = ("is_sent",)
    search_fields = ("subject", "body", "owner")
    permissions = ["can_view_message"]


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "status",
        "start_date",
        "end_date",
        "owner",
    )
    list_filter = ("status",)
    search_fields = (
        "subject",
        "owner",
    )
    filter_horizontal = (
        "messages",
        "recipients",
    )
    permissions = ["can_view_newsletter"]


@admin.register(DeliveryAttempt)
class DeliveryAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "newsletter",
        "status",
        "timestamp",
    )
    list_filter = (
        "status",
        "timestamp",
    )
    search_fields = ("server_response",)
