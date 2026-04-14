from typing import TYPE_CHECKING
from django.conf import settings
from django.db import models
from quotation.choices import QuoteStatus
from quotation.models.managers.quote_model_manager import QuoteModelManager

if TYPE_CHECKING:
    from accounts.models.user_model import UserModel
    from cart.models import CartModel


class QuoteModel(models.Model):
    """ Formal quotation request generated from a cart or direct input. """

    cart: "CartModel | None" = models.ForeignKey(
        "cart.CartModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )
    user: "UserModel | None" = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )
    status = models.CharField(max_length=16, choices=QuoteStatus.choices, default=QuoteStatus.DRAFT)
    customer_name = models.CharField(max_length=255, blank=True, default="")
    customer_email = models.EmailField(blank=True, default="")
    customer_phone = models.CharField(max_length=64, blank=True, default="")
    company_name = models.CharField(max_length=255, blank=True, default="")
    tax_id = models.CharField(max_length=64, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    requested_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: QuoteModelManager = QuoteModelManager()

    id: int
    cart_id: int | None
    user_id: int | None

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Quote"
        verbose_name_plural = "Quotes"

    def __str__(self) -> str:
        """ Return the admin-friendly label for the quote.

        Returns:
            str: Quote label.
        """
        return f"Quote {self.pk}"
