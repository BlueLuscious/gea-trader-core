""" Services for cart expiration lifecycle transitions. """

from django.utils import timezone
from cart.choices import CartStatus
from cart.models import CartModel


class CartExpirationService:
    """ Close active carts whose expiration timestamp has passed. """

    @classmethod
    def close_expired_carts(cls) -> int:
        """ Mark expired active carts as abandoned.

        Returns:
            int: Number of carts updated.
        """
        now = timezone.now()
        return CartModel.objects.active().expired(reference_time=now).update(
            status=CartStatus.ABANDONED,
            updated_at=now,
        )
