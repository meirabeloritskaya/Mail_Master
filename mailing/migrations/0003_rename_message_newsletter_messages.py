# Generated by Django 5.1.2 on 2024-11-04 23:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mailing", "0002_newsletter_start_date_newsletter_subject"),
    ]

    operations = [
        migrations.RenameField(
            model_name="newsletter",
            old_name="message",
            new_name="messages",
        ),
    ]
