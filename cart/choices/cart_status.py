""" Cart lifecycle choices. """

from django.db import models
from django.utils.translation import gettext_lazy as _


class CartStatus(models.TextChoices):
    """ Supported cart lifecycle states. """

    ACTIVE = "active", _("Active")
    CONVERTED = "converted", _("Converted")
    ABANDONED = "abandoned", _("Abandoned")
