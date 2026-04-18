""" Tests for tenant-aware mail reply policy helpers. """

from core.mail import TenantMailReplyPolicy
from core.testing import LoggedSimpleTestCase
from tenancy.models import TenantModel


class TestTenantMailReplyPolicy(LoggedSimpleTestCase):
    """ Verify tenant-aware reply targets are resolved consistently. """

    def test_resolve_customer_reply_to_returns_the_customer_email(self) -> None:
        """ Resolve one customer reply target into a one-item reply-to tuple. """
        self.assertEqual(
            ("customer@example.com",),
            TenantMailReplyPolicy.resolve_customer_reply_to(" customer@example.com "),
        )

    def test_resolve_tenant_contact_reply_to_uses_support_email_first(self) -> None:
        """ Resolve the preferred tenant contact reply target from support email before business email. """
        tenant = TenantModel(
            name="GEA Trader",
            slug="gea-trader",
            business_email="hello@gea-trader.test",
            support_email="support@gea-trader.test",
        )

        self.assertEqual(
            ("support@gea-trader.test",),
            TenantMailReplyPolicy.resolve_tenant_contact_reply_to(tenant),
        )
