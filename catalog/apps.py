from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """ Configure the catalog app. """

    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"
