""" Quote lifecycle choices. """

from django.db import models
from django.utils.translation import gettext_lazy as _


class QuoteStatus(models.TextChoices):
    """ Supported quote lifecycle states. """

    DRAFT = "draft", _("Draft")
    REQUESTED = "requested", _("Requested")
    SENT = "sent", _("Sent")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")
    EXPIRED = "expired", _("Expired")
