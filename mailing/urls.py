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
    path(
        "mailing/<int:pk>/messages/",
        views.message_list,
        name="client_message_list",
    ),
    path("messages/add/", views.message_create, name="message_add"),
    path("messages/", views.all_messages, name="all_messages"),
    path("messages/", views.message_list, name="message_list"),
    path("messages/edit/<int:pk>/", views.message_edit, name="message_edit"),
    path("messages/delete/<int:pk>/", views.message_delete, name="message_delete"),
    path("newsletters/add/", views.newsletter_create, name="newsletter_add"),
    path("newsletters/", views.newsletter_list, name="newsletter_list"),
    path("newsletters/<int:pk>/edit/", views.newsletter_edit, name="newsletter_edit"),
    path(
        "newsletters/delete/<int:pk>/",
        views.newsletter_delete,
        name="newsletter_delete",
    ),
    # path("newsletters/send/<int:client_id>/", views.send_newsletter, name="send_newsletter"),
    path("mailing/<int:pk>/", views.ClientDetailView.as_view(), name="client_detail"),
    path(
        "mailing/newsletters/send/client/<int:client_id>/",
        views.send_newsletter_to_client,
        name="send_newsletter_to_client",
    ),
]
