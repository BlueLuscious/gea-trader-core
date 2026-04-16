from typing import TYPE_CHECKING
from django.db import models
from cart.choices import CartStatus

if TYPE_CHECKING:
    from accounts.models.user_model import UserModel
    from cart.models.cart_model import CartModel
    from tenancy.models import TenantModel


class CartModelQuerySet(models.QuerySet["CartModel"]):
    """ QuerySet for reusable cart filters. """

    def for_tenant(self, tenant: "TenantModel") -> "CartModelQuerySet":
        """ Return carts that belong to one tenant.

        Args:
            tenant: Tenant instance or compatible lookup value.

        Returns:
            CartModelQuerySet: Tenant carts queryset.
        """
        return self.filter(tenant=tenant)

    def active(self) -> "CartModelQuerySet":
        """ Return active carts.

        Returns:
            CartModelQuerySet: Active carts queryset.
        """
        return self.filter(status=CartStatus.ACTIVE)

    def converted(self) -> "CartModelQuerySet":
        """ Return converted carts.

        Returns:
            CartModelQuerySet: Converted carts queryset.
        """
        return self.filter(status=CartStatus.CONVERTED)

    def abandoned(self) -> "CartModelQuerySet":
        """ Return abandoned carts.

        Returns:
            CartModelQuerySet: Abandoned carts queryset.
        """
        return self.filter(status=CartStatus.ABANDONED)

    def for_session(self, session_key: str) -> "CartModelQuerySet":
        """ Return carts bound to a session key.

        Args:
            session_key: Session identifier.

        Returns:
            CartModelQuerySet: Session carts queryset.
        """
        return self.filter(session_key=session_key)

    def for_user(self, user: "UserModel") -> "CartModelQuerySet":
        """ Return carts for a user.

        Args:
            user: User instance or compatible lookup value.

        Returns:
            CartModelQuerySet: User carts queryset.
        """
        return self.filter(user=user)
