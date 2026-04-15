from typing import TYPE_CHECKING
from uuid import UUID
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from quotation.choices import QuoteStatus
from quotation.models.managers.quote_model_manager import QuoteModelManager

if TYPE_CHECKING:
    from accounts.models.user_model import UserModel
    from cart.models import CartModel
    from tenancy.models import TenantModel


class QuoteModel(models.Model):
    """ Formal quotation request generated from a cart or direct input. """

    tenant: "TenantModel" = models.ForeignKey(
        "tenancy.TenantModel",
        on_delete=models.CASCADE,
        related_name="quotes",
        verbose_name=_("Business"),
        help_text=_("Business that owns this quote and the follow-up around it."),
    )
    cart: "CartModel | None" = models.ForeignKey(
        "cart.CartModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
        verbose_name=_("Source cart"),
        help_text=_("Optional cart that originated this quote."),
    )
    user: "UserModel | None" = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
        verbose_name=_("Customer account"),
        help_text=_("Optional customer account related to this quote."),
    )
    status = models.CharField(
        max_length=16,
        choices=QuoteStatus.choices,
        default=QuoteStatus.DRAFT,
        verbose_name=_("Quote status"),
        help_text=_("Current stage of this quote in your sales follow-up."),
    )
    customer_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Customer name"),
        help_text=_("Name of the person requesting the quote."),
    )
    customer_email = models.EmailField(
        blank=True,
        default="",
        verbose_name=_("Customer email"),
        help_text=_("Email address your team can use to follow up on this quote."),
    )
    customer_phone = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("Customer phone"),
        help_text=_("Phone number your team can use to follow up on this quote."),
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Company"),
        help_text=_("Optional company name when the quote belongs to a business customer."),
    )
    tax_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("Tax ID"),
        help_text=_("Optional tax or company identification reference."),
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Internal notes"),
        help_text=_("Private context for your team. Customers do not need to see this text."),
    )
    requested_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Requested at"),
        help_text=_("When the quote was formally requested."),
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Sent at"),
        help_text=_("When the quote was sent back to the customer."),
    )
    answered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Answered at"),
        help_text=_("When the customer answered this quote."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("When this quote was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("When this quote was last updated."),
    )

    objects: QuoteModelManager = QuoteModelManager()

    id: int
    tenant_id: UUID
    cart_id: int | None
    user_id: int | None

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Quote")
        verbose_name_plural = _("Quotes")

    def __str__(self) -> str:
        """ Return the admin-friendly label for the quote.

        Returns:
            str: Quote label.
        """
        return f"Quote {self.pk}"
