""" Cart persistence model for tenant-scoped runtime basket state. """

from typing import TYPE_CHECKING
from uuid import UUID
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from cart.choices import CartStatus
from cart.models.managers.cart_model_manager import CartModelManager

if TYPE_CHECKING:
    from accounts.models.user_model import UserModel
    from tenancy.models import TenantModel


class CartModel(models.Model):
    """ Persisted cart used as backing store for the quotation basket. """

    tenant: "TenantModel" = models.ForeignKey(
        "tenancy.TenantModel",
        on_delete=models.CASCADE,
        related_name="carts",
        verbose_name=_("Business"),
        help_text=_("Business that owns this cart and the runtime activity around it."),
    )
    user: "UserModel | None" = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts",
        verbose_name=_("Customer account"),
        help_text=_("Optional customer account currently associated with this cart."),
    )
    session_key = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("Session key"),
        help_text=_("Session identifier used when the cart is not tied to a signed-in customer account."),
    )
    status = models.CharField(
        max_length=16,
        choices=CartStatus.choices,
        default=CartStatus.ACTIVE,
        verbose_name=_("Cart status"),
        help_text=_("Current lifecycle stage of this cart in the runtime flow."),
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Expires at"),
        help_text=_("Optional expiration timestamp used by runtime cleanup or follow-up rules."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("When this cart was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("When this cart was last updated."),
    )

    objects: CartModelManager = CartModelManager()

    id: int
    tenant_id: UUID
    user_id: int | None

    class Meta:
        """ Declarative admin-facing metadata for cart persistence. """

        ordering = ("-updated_at", "-created_at")
        constraints = [
            models.CheckConstraint(
                condition=Q(user__isnull=False) | ~Q(session_key=""),
                name="cart_requires_user_or_session_key",
            ),
        ]
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")

    def __str__(self) -> str:
        """ Return the admin-friendly label for the cart.

        Returns:
            str: Cart label.
        """
        return f"{_('Cart')} {self.pk}"
