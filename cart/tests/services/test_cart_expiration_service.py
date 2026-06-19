""" Tests for cart expiration services. """

from django.utils import timezone
from core.testing.base import LoggedTestCase
from cart.choices import CartStatus
from cart.models import CartModel
from cart.services import CartExpirationService
from tenancy.models import TenantModel


class TestCartExpirationService(LoggedTestCase):
    """ Verify cart expiration lifecycle transitions. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for cart expiration fixtures.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_close_expired_carts_marks_only_expired_active_carts_as_abandoned(self) -> None:
        """ Verify expired active carts are abandoned without touching future or converted carts. """
        now = timezone.now()
        tenant = self._create_tenant("cart-expiration-service")
        expired_active_cart = CartModel.objects.create(
            tenant=tenant,
            session_key="expired-active",
            status=CartStatus.ACTIVE,
            expires_at=now - timezone.timedelta(minutes=1),
        )
        future_active_cart = CartModel.objects.create(
            tenant=tenant,
            session_key="future-active",
            status=CartStatus.ACTIVE,
            expires_at=now + timezone.timedelta(minutes=1),
        )
        converted_expired_cart = CartModel.objects.create(
            tenant=tenant,
            session_key="converted-expired",
            status=CartStatus.CONVERTED,
            expires_at=now - timezone.timedelta(minutes=1),
        )

        closed_count = CartExpirationService.close_expired_carts()

        self.assertEqual(1, closed_count)
        expired_active_cart.refresh_from_db()
        future_active_cart.refresh_from_db()
        converted_expired_cart.refresh_from_db()
        self.assertEqual(CartStatus.ABANDONED, expired_active_cart.status)
        self.assertEqual(CartStatus.ACTIVE, future_active_cart.status)
        self.assertEqual(CartStatus.CONVERTED, converted_expired_cart.status)

