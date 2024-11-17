# mailing/management/commands/send_newsletter.py
from django.core.management.base import BaseCommand, CommandError
from mailing.models import Newsletter
from mailing.views import send_newsletter  # Функция отправки из utils


class Command(BaseCommand):
    help = "Send a specific newsletter by its ID"

    def add_arguments(self, parser):
        parser.add_argument(
            "newsletter_id", type=int, help="ID of the newsletter to send"
        )

    def handle(self, *args, **kwargs):
        newsletter_id = kwargs["newsletter_id"]
        try:
            newsletter = Newsletter.objects.get(id=newsletter_id)
            send_newsletter(newsletter)  # вызов функции отправки
            self.stdout.write(
                self.style.SUCCESS(f"Newsletter {newsletter_id} sent successfully.")
            )
        except Newsletter.DoesNotExist:
            raise CommandError(f"Newsletter with ID {newsletter_id} does not exist.")
        except Exception as e:
            raise CommandError(
                f"An error occurred while sending newsletter {newsletter_id}: {e}"
            )
