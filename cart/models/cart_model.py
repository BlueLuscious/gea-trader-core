from typing import TYPE_CHECKING
from uuid import UUID
from django.conf import settings
from django.db import models
from django.db.models import Q
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
    )
    user: "UserModel | None" = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts",
    )
    session_key = models.CharField(max_length=64, blank=True, default="")
    status = models.CharField(max_length=16, choices=CartStatus.choices, default=CartStatus.ACTIVE)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: CartModelManager = CartModelManager()
    
    id: int
    tenant_id: UUID
    user_id: int | None

    class Meta:
        ordering = ("-updated_at", "-created_at")
        constraints = [
            models.CheckConstraint(
                condition=Q(user__isnull=False) | ~Q(session_key=""),
                name="cart_requires_user_or_session_key",
            ),
        ]
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self) -> str:
        """ Return the admin-friendly label for the cart.

        Returns:
            str: Cart label.
        """
        return f"Cart {self.pk}"
