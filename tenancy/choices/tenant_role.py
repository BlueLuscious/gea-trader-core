""" Role choices for tenant memberships. """

from django.db import models
from django.utils.translation import gettext_lazy as _


class TenantRole(models.TextChoices):
    """ Reusable roles describing a user's relationship with a tenant. """

    MASTER = "master", _("Master")
    OWNER = "owner", _("Owner")
    OPERATOR = "operator", _("Operator")
