from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CatalogConfig(AppConfig):
    """ Configure the catalog app. """

    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"
    verbose_name = _("Catalog")
