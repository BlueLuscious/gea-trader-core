from django.apps import AppConfig


class CartConfig(AppConfig):
    """ Configure the cart app. """

    default_auto_field = "django.db.models.BigAutoField"
    name = "cart"
