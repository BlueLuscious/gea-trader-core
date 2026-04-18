""" App configuration for the tenancy domain. """

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TenancyConfig(AppConfig):
    """ Django app configuration for tenant models and active-tenant flows. """

    default_auto_field = "django.db.models.BigAutoField"
    name = "tenancy"
    verbose_name = _("Business access")
