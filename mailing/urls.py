from django.urls import path
from . import views

app_name = "mailing"

urlpatterns = [
    path("", views.home, name="home"),
    path("mailing/", views.ClientListView.as_view(), name="client_list"),
    path("mailing/add/", views.ClientCreateView.as_view(), name="client_add"),
    path(
        "mailing/<int:pk>/edit/", views.ClientUpdateView.as_view(), name="client_edit"
    ),
    path("mailing/<int:pk>/", views.ClientDetailView.as_view(), name="client_detail"),
    path(
        "mailing/<int:pk>/delete/",
        views.ClientDeleteView.as_view(),
        name="client_delete",
    ),
    path("mailing/<int:client_id>/messages/", views.MessageClientView.as_view(), name="client_message_list"),
    path("messages/add/", views.MessageCreateView.as_view(), name="message_add"),
    path("messages/", views.MessagesListView.as_view(), name="message_list"),
    path("messages/edit/<int:pk>/", views.MessageEditView.as_view(), name="message_edit"),
    path("messages/delete/<int:pk>/", views.MessageDeleteView.as_view(), name="message_delete"),
    path("newsletters/add/", views.NewsletterCreateView.as_view(), name="newsletter_add"),
    path("newsletters/", views.NewsletterListView.as_view(), name="newsletter_list"),
    path("newsletters/<int:pk>/edit/", views.NewsletterUpdateView.as_view(), name="newsletter_edit"),
    path(
        "newsletters/delete/<int:pk>/",
        views.NewsletterDeleteView.as_view(),
        name="newsletter_delete",
    ),
    path(
        "mailing/newsletters/send/client/<int:client_id>/",
        views.send_newsletter_to_client,
        name="send_newsletter_to_client",
    ),
    path("newsletters/send/<int:pk>/", views.send_newsletter, name="send_newsletter"),
]
