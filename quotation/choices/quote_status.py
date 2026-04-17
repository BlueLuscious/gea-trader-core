""" Quote workflow choices. """

from django.db import models
from django.utils.translation import gettext_lazy as _


class QuoteWorkflowStatus(models.TextChoices):
    """ Supported internal quote workflow states. """

    DRAFT = "draft", _("Draft")
    REQUESTED = "requested", _("Requested")
    IN_PROGRESS = "in_progress", _("In progress")
    COMPLETED = "completed", _("Completed")
    CANCELLED = "cancelled", _("Cancelled")
