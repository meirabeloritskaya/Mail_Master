from django.urls import path
from .views import UserCreateView, CustomLoginView, CustomLogoutView, email_verification

app_name = "users"

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
]
