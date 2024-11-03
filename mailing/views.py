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


def client_add(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("mailing:client_list")
    else:
        form = ClientForm()
    return render(request, "mailing/client_form.html", {"form": form})


def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("mailing:client_list")
    else:
        form = ClientForm(instance=client)
    return render(request, "mailing/client_form.html", {"form": form, "client": client})


class ClientDetailView(DetailView):
    model = Client
    template_name = "mailing/client_detail.html"
    context_object_name = "client"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем клиента, объект которого представлен в DetailView
        client = self.object

        # Все сообщения, связанные с клиентом через его рассылки
        # context["all_messages"] = Message.objects.filter(newsletters__in=client.newsletters.all())

        # Добавляем также отдельный список сообщений с учетом других критериев, если это нужно
        context["client_messages"] = Message.objects.filter(
            newsletters__recipients=client
        )

        context["unassigned_messages"] = Message.objects.exclude(
            newsletters__recipients=client
        )
        # Можно передать и темы сообщений, если они специфичны

        context["title_messages"] = Message.objects.filter(
            newsletters__subject__in=client.newsletters.values("subject")
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
            send_email(
                client.email, message.subject, message.body
            )  # Реализация send_email должна быть определена отдельно

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


def message_create(request):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("mailing:all_messages")
    else:
        form = MessageForm()
    return render(request, "mailing/message_form.html", {"form": form})


def all_messages(request):
    messages = Message.objects.all()
    return render(request, "mailing/all_messages.html", {"messages": messages})


def message_list(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    messages = Message.objects.filter(client=client)
    return render(
        request, "mailing/message_list.html", {"messages": messages, "client": client}
    )


def message_edit(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.method == "POST":
        message.subject = request.POST["subject"]
        message.body = request.POST["body"]
        message.save()
        return redirect("mailing:message_list")
    return render(request, "mailing/message_edit.html", {"message": message})


def message_delete(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.method == "POST":
        message.delete()
        return redirect("mailing:message_list")
    return render(request, "mailing/message_delete.html", {"message": message})


def newsletter_create(request):
    clients = Client.objects.all()
    messages = Message.objects.all()

    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():

            newsletter = form.save(commit=False)
            newsletter.save()

            message_ids = request.POST.getlist("messages")
            recipient_ids = request.POST.getlist("recipients")
            newsletter.message.set(message_ids)
            newsletter.recipients.set(recipient_ids)
            newsletter.save()
            return redirect("mailing:newsletter_list")
        else:
            print(form.errors)
    else:
        form = NewsletterForm()
        clients = Client.objects.all()
        messages = Message.objects.all()
    return render(
        request,
        "mailing/newsletter_form.html",
        {"form": form, "clients": clients, "messages": messages},
    )


def newsletter_edit(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    clients = Client.objects.all()
    messages = Message.objects.all()

    if request.method == "POST":
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            newsletter = form.save(commit=False)

            # Получаем выбранные сообщения и получателей
            selected_messages = request.POST.getlist("messages")
            selected_recipients = request.POST.getlist("recipients")

            # Обновляем сообщения
            newsletter.save()  # Сначала сохраняем рассылку
            newsletter.message.set(
                selected_messages
            )  # Устанавливаем выбранные сообщения
            newsletter.recipients.set(selected_recipients)  # Устанавливаем получателей

            return redirect("mailing:newsletter_list")
    else:
        form = NewsletterForm(instance=newsletter)

    return render(
        request,
        "mailing/newsletter_form.html",
        {
            "form": form,
            "clients": clients,
            "messages": messages,
            "newsletter": newsletter,
        },
    )


def newsletter_list(request):
    newsletters = Newsletter.objects.all()
    return render(request, "mailing/newsletter_list.html", {"newsletters": newsletters})


def newsletter_delete(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.method == "POST":
        newsletter.delete()
        return redirect("mailing:newsletter_list")
    return render(request, "mailing/newsletter_delete.html", {"newsletter": newsletter})


def send_email(to_email, subject, message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )


#
# def send_newsletter(newsletter, recipient_email):
#     try:
#         send_mail(
#             subject=newsletter.subject,
#             message=newsletter.message,
#             from_email="meiramirth@example.com",
#             recipient_list=[recipient_email],
#         )
#         DeliveryAttempt.objects.create(
#             newsletter=newsletter,
#             status="success",
#             server_response="Successfully sent"
#         )
#     except Exception as e:
#         # Сохраняем текст ошибки в server_response
#         DeliveryAttempt.objects.create(
#             newsletter=newsletter,
#             status="failed",
#             server_response=str(e)  # Сохраняем текст ошибки
#         )
#


def send_newsletter_to_client(request, pk, client_id):
    # Получаем клиента и рассылку
    client = get_object_or_404(Client, pk=client_id)
    newsletter = get_object_or_404(Newsletter, pk=pk)

    # Получаем список сообщений для рассылки
    selected_messages = newsletter.message.all()

    # Отправляем выбранные сообщения клиенту
    for message in selected_messages:
        send_email(client.email, message.subject, message.body)

    messages.success(
        request, "Сообщения из выбранной рассылки были отправлены клиенту."
    )
    return redirect("mailing:client_detail", pk=client.pk)


def send_newsletter(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    recipients = newsletter.recipients.all()
    for recipient in recipients:
        try:
            send_mail(
                subject=newsletter.subject,
                message=newsletter.message,
                from_email="meiramirth@example.com",
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            DeliveryAttempt.objects.create(
                newsletter=newsletter, timestamp=timezone.now(), status="success"
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


def send_newsletter_view(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    send_newsletter(newsletter)
    return redirect("newsletter_list")
