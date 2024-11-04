from django.contrib import admin
from .models import Client, Message, Newsletter, DeliveryAttempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "comment")
    search_fields = ("email", "full_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "is_sent", "client")
    list_filter = ("is_sent",)
    search_fields = ("subject", "body")


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("subject", "status", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("subject",)
    filter_horizontal = ("messages", "recipients")


@admin.register(DeliveryAttempt)
class DeliveryAttemptAdmin(admin.ModelAdmin):
    list_display = ("newsletter", "status", "timestamp")
    list_filter = ("status", "timestamp")
    search_fields = ("server_response",)
