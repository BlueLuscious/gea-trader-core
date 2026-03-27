""" Quote lifecycle choices. """

from django.db import models


class QuoteStatus(models.TextChoices):
    """ Supported quote lifecycle states. """

    DRAFT = "draft", "Draft"
    REQUESTED = "requested", "Requested"
    SENT = "sent", "Sent"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    EXPIRED = "expired", "Expired"
