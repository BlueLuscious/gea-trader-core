""" Application configuration for the accounts domain. """

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """ Django application configuration for accounts. """

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
