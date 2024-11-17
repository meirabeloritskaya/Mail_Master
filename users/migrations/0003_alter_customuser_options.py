from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Newsletter


def add_permissions(apps, schema_editor):

    manager_group = Group.objects.get(name="Менеджер")

    disable_newsletter_permission = Permission.objects.get(
        codename="disable_newsletter",
        content_type=ContentType.objects.get_for_model(Newsletter),
    )

    manager_group.permissions.add(disable_newsletter_permission)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_customuser_options_remove_customuser_username_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="customuser",
            options={
                "permissions": [("block_user", "Can block users")],
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
            },
        ),
        migrations.RunPython(add_permissions),
    ]
