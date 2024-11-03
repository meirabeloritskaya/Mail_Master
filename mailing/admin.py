from django.contrib import admin
from .models import Newsletter, DeliveryAttempt


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("subject", "start_date", "end_date")


@admin.register(DeliveryAttempt)
class DeliveryAttemptAdmin(admin.ModelAdmin):
    list_display = ("newsletter", "timestamp", "status", "server_response")
