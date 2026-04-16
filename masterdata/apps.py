from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MasterdataConfig(AppConfig):
    """ Configure the masterdata app. """

    default_auto_field = "django.db.models.BigAutoField"
    name = "masterdata"
    verbose_name = _("Reference data")

