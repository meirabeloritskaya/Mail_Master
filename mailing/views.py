from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import Client, Message, Newsletter, DeliveryAttempt
from .forms import ClientForm, MessageForm, NewsletterForm
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from users.models import CustomUser


def home(request):
    # Проверка, является ли пользователь менеджером
    is_manager = request.user.groups.filter(name='Менеджер').exists()

    # Статистика, доступная всем пользователям
    total_newsletters = Newsletter.objects.count()
    active_newsletters = Newsletter.objects.filter(status="running").count()
    unique_recipients = Client.objects.count()

    # Дополнительная статистика для менеджера
    total_clients = Client.objects.count()
    total_users = CustomUser.objects.count()  # если есть модель владельцев
    total_messages = Message.objects.count()

    # Контекст для шаблона
    context = {
        'is_manager': is_manager,
        'total_newsletters': total_newsletters,
        'active_newsletters': active_newsletters,
        'unique_recipients': unique_recipients,
    }

    # Если это менеджер, добавляем общую статистику
    if is_manager:
        context.update({
            'total_clients': total_clients,
            'total_owners': total_users,
            'total_messages': total_messages,
            'total_newsletters': total_newsletters,
        })

    return render(request, 'mailing/home.html', context)


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


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        if (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="Менеджер").exists()
        ):
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        client = self.get_object()

        if not self.user_has_permission(client):
            messages.error(
                self.request, "У вас нет прав на редактирование информации о клиенте."
            )
            return HttpResponseRedirect(
                self.request.META.get("HTTP_REFERER", self.success_url)
            )
        return super().form_valid(form)

    def user_has_permission(self, product):

        return (
            self.request.user == product.owner
            or self.request.user.has_perm("mailing.can_change_client")
            or self.request.user.groups.filter(name="Пользователь").exists()
        )


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")

    def post(self, request, *args, **kwargs):
        client = self.get_object()

        if not self.user_has_permission(client):
            messages.error(request, "У вас нет прав на удаление информации о клиенте.")
            return HttpResponseRedirect(
                request.META.get("HTTP_REFERER", self.success_url)
            )
        return super().post(request, *args, **kwargs)

    def user_has_permission(self, product):

        return (
            self.request.user == product.owner
            or self.request.user.has_perm("mailing.can_delete_client")
            or self.request.user.groups.filter(name="Пользователь").exists()
        )


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessagesListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "message_list"

    def get_queryset(self):
        if (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="Менеджер").exists()
        ):
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


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

    def form_valid(self, form):
        message = self.get_object()

        if not self.user_has_permission(message):
            messages.error(self.request, "У вас нет прав на редактирование продукта.")
            return HttpResponseRedirect(
                self.request.META.get("HTTP_REFERER", self.success_url)
            )
        return super().form_valid(form)

    def user_has_permission(self, product):

        return (
            self.request.user == product.owner
            or self.request.user.has_perm("mailing.can_change_message")
            or self.request.user.groups.filter(name="Пользователь").exists()
        )


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "mailing/message_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def post(self, request, *args, **kwargs):
        message = self.get_object()

        if not self.user_has_permission(message):
            messages.error(request, "У вас нет прав на удаление сообщения.")
            return HttpResponseRedirect(
                request.META.get("HTTP_REFERER", self.success_url)
            )
        return super().post(request, *args, **kwargs)

    def user_has_permission(self, product):

        return (
            self.request.user == product.owner
            or self.request.user.has_perm("mailing.can_delete_message")
            or self.request.user.groups.filter(name="Пользователь").exists()
        )


class NewsletterCreateView(LoginRequiredMixin, CreateView):
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


class NewsletterListView(LoginRequiredMixin, ListView):
    model = Newsletter
    template_name = "mailing/newsletter_list.html"
    context_object_name = "newsletters"

    def get_queryset(self):
        if (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="Менеджер").exists()
        ):
            return Newsletter.objects.all()
        return Newsletter.objects.filter(owner=self.request.user).prefetch_related(
            "messages", "recipients"
        )


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

    def get_queryset(self):
        if (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="Менеджер").exists()
        ):
            return DeliveryAttempt.objects.all()
        return DeliveryAttempt.objects.filter(newsletter__owner=self.request.user)


class ClientBlockView(PermissionRequiredMixin, UpdateView):
    model = Client
    fields = ["is_blocked"]
    template_name = "client_block.html"
    permission_required = "mailing.can_block_client"

    def get_success_url(self):
        return self.object.get_absolute_url()


class NewsletterDeactivateView(PermissionRequiredMixin, UpdateView):
    model = Newsletter
    fields = ["status"]
    template_name = "newsletter_deactivate.html"
    permission_required = "mailing.can_deactivate_newsletter"

    def form_valid(self, form):
        form.instance.status = "completed"
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()
