""" Application configuration for the accounts domain. """

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    """ Django application configuration for accounts. """

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = _("Accounts")
