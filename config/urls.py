
from django.contrib import admin
from django.urls import path, include
from mailing import views as mailing_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", mailing_views.home, name="home"),  # URL для главной страницы
    path("mailing/", include("mailing.urls")),  # Остальные маршруты приложения mailing
]
