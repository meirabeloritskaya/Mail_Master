from users.forms import CustomUserCreationForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.views.generic import CreateView
from users.models import CustomUser
from django.urls import reverse_lazy
from config.settings import EMAIL_HOST_USER
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
import secrets


class UserCreateView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()

        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}"
        send_mail(
            subject="Подтверждение почты",
            message=f"Привет, перейди по ссылке {url} для подтверждления почты",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class CustomLoginView(LoginView):

    template_name = "users/login.html"
    redirect_authenticated_user = True
    success_url = settings.LOGIN_REDIRECT_URL


class CustomLogoutView(LogoutView):
    template_name = ""
