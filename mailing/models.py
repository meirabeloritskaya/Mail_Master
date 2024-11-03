from django.db import models
from django.utils import timezone


class Client(models.Model):
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


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="messages", null=True
    )
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.subject


class Newsletter(models.Model):
    # client = models.ForeignKey(Client, related_name='newsletters', on_delete=models.CASCADE, null=True)
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("running", "Запущена"),
        ("completed", "Завершена"),
    ]
    subject = models.CharField(max_length=200, default="Без темы")
    start_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="created")

    message = models.ManyToManyField(Message, related_name="newsletters", blank=True)
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
        return f"Newsletter: {', '.join(message.subject for message in self.message.all()) if self.message.exists() else 'Нет сообщений'}"

    def start_sending(self):
        self.status = "running"
        self.sent_date = timezone.now()
        self.save()

    def complete_sending(self):
        self.status = "completed"
        self.save()


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
