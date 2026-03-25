""" Cart lifecycle choices. """

from django.db import models


class CartStatus(models.TextChoices):
    """ Supported cart lifecycle states. """

    ACTIVE = "active", "Active"
    CONVERTED = "converted", "Converted"
    ABANDONED = "abandoned", "Abandoned"
