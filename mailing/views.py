from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.shortcuts import render, redirect, get_object_or_404
from .models import Client, Message, Newsletter, DeliveryAttempt
from .forms import ClientForm, MessageForm, NewsletterForm
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib import messages


def home(request):
    # Количество всех рассылок
    total_newsletters = Newsletter.objects.count()

    # Количество активных рассылок со статусом "запущено"
    active_newsletters = Newsletter.objects.filter(status="running").count()

    # Количество уникальных получателей
    unique_recipients = Client.objects.all().count()

    context = {
        "total_newsletters": total_newsletters,
        "active_newsletters": active_newsletters,
        "unique_recipients": unique_recipients,
    }

    return render(request, "mailing/home.html", context)


class ClientDetailView(DetailView):
    model = Client
    template_name = "mailing/client_detail.html"
    context_object_name = "client"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем клиента, объект которого представлен в DetailView
        client = self.object

        context["related_messages"] = self.object.messages.all()

        context["client_message_list"] = Message.objects.filter(
            newsletters__recipients=client
        )
        context["unassigned_messages"] = Message.objects.exclude(
            newsletters__recipients=client
        )

        return context

    def post(self, request, *args, **kwargs):
        # Получаем объект клиента из DetailView
        self.object = self.get_object()
        client = self.object

        # Извлекаем ID выбранных сообщений из формы
        message_ids = request.POST.getlist("messages")
        selected_messages = Message.objects.filter(id__in=message_ids)

        # Отправляем выбранные сообщения клиенту
        for message in selected_messages:
            send_email(client.email, message.subject, message.body)

        # Отображаем сообщение об успешной отправке
        messages.success(request, "Выбранные сообщения были отправлены клиенту.")
        return redirect("mailing:client_detail", pk=client.pk)


class ClientListView(ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessagesListView(ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "message_list"


class MessageClientView(ListView):
    template_name = "mailing/client_message_list.html"
    context_object_name = "client_message_list"

    def get_queryset(self):
        self.client = get_object_or_404(Client, id=self.kwargs["client_id"])
        return Message.objects.filter(client=self.client)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["client"] = self.client
        return context


class MessageEditView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_edit.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "mailing/message_delete.html"
    success_url = reverse_lazy("mailing:message_list")


class NewsletterCreateView(CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "mailing/newsletter_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["clients"] = Client.objects.all()
        context["messages"] = Message.objects.all()
        return context

    def form_valid(self, form):
        newsletter = form.save(commit=False)

        # Сначала сохраняем рассылку
        newsletter.save()

        # Получаем выбранные сообщения и получателей
        message_ids = self.request.POST.getlist("messages")
        recipient_ids = self.request.POST.getlist("recipients")
        newsletter.messages.set(message_ids)  # Устанавливаем выбранные сообщения
        newsletter.recipients.set(recipient_ids)  # Устанавливаем получателей

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("mailing:newsletter_list")


class NewsletterUpdateView(UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "mailing/newsletter_form.html"
    context_object_name = "newsletter"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["clients"] = Client.objects.all()
        context["messages"] = Message.objects.all()
        return context

    def form_valid(self, form):
        newsletter = form.save(commit=False)

        # Получаем выбранные сообщения и получателей
        selected_messages = self.request.POST.getlist("messages")
        selected_recipients = self.request.POST.getlist("recipients")

        # Сначала сохраняем рассылку
        newsletter.save()
        newsletter.messages.set(selected_messages)  # Устанавливаем выбранные сообщения
        newsletter.recipients.set(selected_recipients)  # Устанавливаем получателей

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("mailing:newsletter_list")


class NewsletterListView(ListView):
    model = Newsletter
    template_name = "mailing/newsletter_list.html"
    context_object_name = "newsletters"

    def get_queryset(self):
        return Newsletter.objects.prefetch_related("messages", "recipients")


class NewsletterDeleteView(DeleteView):
    model = Newsletter
    template_name = "mailing/newsletter_delete.html"
    context_object_name = "newsletter"
    success_url = reverse_lazy("mailing:newsletter_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.get_success_url())


def send_email(to_email, subject, message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )


def send_newsletter(request, pk):

    newsletter = get_object_or_404(Newsletter, pk=pk)

    recipients = newsletter.recipients.all()

    selected_messages = newsletter.messages.all()

    for recipient in recipients:
        try:
            # Отправляем выбранные сообщения клиенту
            for message in selected_messages:
                send_email(recipient.email, message.subject, message.body)

            DeliveryAttempt.objects.create(
                newsletter=newsletter,
                timestamp=timezone.now(),
                status="success",
                server_response="Сообщение успешно отправлено",
            )
        except Exception as e:

            DeliveryAttempt.objects.create(
                newsletter=newsletter,
                timestamp=timezone.now(),
                status="failed",
                server_response=str(e),
            )
            messages.error(
                request, f"Ошибка при отправке для {recipient.email}: {str(e)}"
            )

    messages.success(request, "Рассылка успешно отправлена!")
    return redirect("mailing:newsletter_list")


class DeliveryAttemptListView(ListView):
    model = DeliveryAttempt
    template_name = "mailing/delivery_attempts_list.html"
    context_object_name = "attempts"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["success_count"] = DeliveryAttempt.objects.filter(
            status="success"
        ).count()
        context["failed_count"] = DeliveryAttempt.objects.filter(
            status="failed"
        ).count()
        return context


#
