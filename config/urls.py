from django.contrib import admin
from django.urls import path, include
from mailing import views as mailing_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", mailing_views.home, name="home"),
    path("mailing/", include("mailing.urls")),
    path("users/", include(("users.urls", "users"), namespace="users")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
