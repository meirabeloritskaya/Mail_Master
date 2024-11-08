# Generated by Django 5.1.2 on 2024-10-31 17:57

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="Email"
                    ),
                ),
                ("full_name", models.CharField(max_length=100, verbose_name="Ф.И.О.")),
                ("comment", models.TextField(blank=True, verbose_name="Комментарий")),
            ],
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subject", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("is_sent", models.BooleanField(default=False)),
                (
                    "client",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="mailing.client",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Newsletter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sent_date", models.DateTimeField(blank=True, null=True)),
                ("end_date", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("created", "Создана"),
                            ("running", "Запущена"),
                            ("completed", "Завершена"),
                        ],
                        default="created",
                        max_length=10,
                    ),
                ),
                (
                    "message",
                    models.ManyToManyField(
                        blank=True, related_name="newsletters", to="mailing.message"
                    ),
                ),
                ("recipients", models.ManyToManyField(blank=True, to="mailing.client")),
            ],
        ),
        migrations.CreateModel(
            name="DeliveryAttempt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "status",
                    models.CharField(
                        choices=[("success", "Успешно"), ("failed", "Не успешно")],
                        max_length=10,
                    ),
                ),
                ("server_response", models.TextField(blank=True, null=True)),
                (
                    "newsletter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="delivery_attempts",
                        to="mailing.newsletter",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="client",
            name="newsletters",
            field=models.ManyToManyField(
                related_name="mailing", to="mailing.newsletter"
            ),
        ),
    ]