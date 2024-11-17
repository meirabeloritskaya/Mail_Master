from django.conf import settings
from django.db import models
from django.utils import timezone


class Client(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="owned_clients",
        null=True,
    )
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=100, verbose_name="Ф.И.О.")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    newsletters = models.ManyToManyField("Newsletter", related_name="mailing")

    def __str__(self):
        return self.full_name

    def get_all_messages(self):
        # Получаем все сообщения, связанные с рассылками этого клиента
        messages = Message.objects.filter(newsletter__in=self.newsletters.all())
        return messages

    class Meta:
        verbose_name = "клиент"
        verbose_name_plural = "клиенты"
        ordering = ["full_name"]
        permissions = [
            ("can_view_client", "Может просматривать клиентов"),
            ("can_block_client", "Может заблокировать клиента"),
        ]


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="messages", null=True
    )
    is_sent = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="owned_messages",
        null=True,
    )

    def __str__(self):
        return self.subject

    class Meta:
        permissions = [
            ("can_view_message", "Может просматривать сообщения"),
        ]


class Newsletter(models.Model):

    STATUS_CHOICES = [
        ("created", "Создана"),
        ("running", "Запущена"),
        ("completed", "Завершена"),
    ]
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="owned_newsletters",
        null=True,
    )
    subject = models.CharField(max_length=200, default="Без темы")
    start_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="created")

    messages = models.ManyToManyField(Message, related_name="newsletters", blank=True)
    recipients = models.ManyToManyField(Client, blank=True)

    def save(self, *args, **kwargs):
        current_time = timezone.now()
        if self.sent_date and current_time < self.sent_date:
            self.status = "created"
        elif self.sent_date <= current_time <= self.end_date:
            self.status = "running"
        else:
            self.status = "completed"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Newsletter: {', '.join(message.subject for message in self.messages.all()) if self.messages.exists() else 'Нет сообщений'}"

    def start_sending(self):
        self.status = "running"
        self.sent_date = timezone.now()
        self.save()

    def complete_sending(self):
        self.status = "completed"
        self.save()

    class Meta:
        permissions = [
            ("can_view_client", "Может просматривать рассылку"),
            ("can_deactivate_newsletter", "Может деактивировать рассылку"),
        ]


class DeliveryAttempt(models.Model):
    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]

    # Дата и время попытки отправки
    timestamp = models.DateTimeField(default=timezone.now)

    # Статус попытки отправки
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    # Ответ почтового сервера (в случае ошибки)
    server_response = models.TextField(blank=True, null=True)

    # Внешний ключ на модель рассылки
    newsletter = models.ForeignKey(
        "Newsletter", on_delete=models.CASCADE, related_name="delivery_attempts"
    )

    def __str__(self):
        return f"{self.newsletter} - {self.get_status_display()} at {self.timestamp}"
