from typing import TYPE_CHECKING
from django.db import models
from cart.models.querysets.cart_model_queryset import CartModelQuerySet

if TYPE_CHECKING:
    from accounts.models.user_model import UserModel
    from cart.models.cart_model import CartModel
    from tenancy.models import TenantModel


class CartModelManager(models.Manager["CartModel"]):
    """ Manager exposing typed cart queryset helpers. """

    def get_queryset(self) -> "CartModelQuerySet":
        """ Return the base queryset for cart queries.

        Returns:
            CartModelQuerySet: Specialized queryset for carts.
        """
        return CartModelQuerySet(self.model, using=self._db)

    def active(self) -> "CartModelQuerySet":
        """ Return active carts.

        Returns:
            CartModelQuerySet: Active carts queryset.
        """
        return self.get_queryset().active()

    def for_tenant(self, tenant: "TenantModel") -> "CartModelQuerySet":
        """ Return carts for one tenant.

        Args:
            tenant: Tenant instance or compatible lookup value.

        Returns:
            CartModelQuerySet: Tenant carts queryset.
        """
        return self.get_queryset().for_tenant(tenant)

    def converted(self) -> "CartModelQuerySet":
        """ Return converted carts.

        Returns:
            CartModelQuerySet: Converted carts queryset.
        """
        return self.get_queryset().converted()

    def abandoned(self) -> "CartModelQuerySet":
        """ Return abandoned carts.

        Returns:
            CartModelQuerySet: Abandoned carts queryset.
        """
        return self.get_queryset().abandoned()

    def for_session(self, session_key: str) -> "CartModelQuerySet":
        """ Return carts for a session key.

        Args:
            session_key: Session identifier.

        Returns:
            CartModelQuerySet: Session carts queryset.
        """
        return self.get_queryset().for_session(session_key)

    def for_user(self, user: "UserModel") -> "CartModelQuerySet":
        """ Return carts for a user.

        Args:
            user: User instance or compatible lookup value.

        Returns:
            CartModelQuerySet: User carts queryset.
        """
        return self.get_queryset().for_user(user)
