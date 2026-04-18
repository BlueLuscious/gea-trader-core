""" Tests for tenant-aware mail recipient resolution. """

from core.mail import TenantMailRecipientResolver
from core.testing import LoggedSimpleTestCase
from tenancy.models import TenantBrandingModel, TenantModel


class TestTenantMailRecipientResolver(LoggedSimpleTestCase):
    """ Verify tenant-facing contact recipients resolve from tenant metadata. """

    def test_resolve_contact_email_prefers_support_email(self) -> None:
        """ Resolve the preferred contact email from support email before business email. """
        tenant = TenantModel(
            name="GEA Trader",
            slug="gea-trader",
            business_email="hello@gea-trader.test",
            support_email="support@gea-trader.test",
        )

        self.assertEqual(
            "support@gea-trader.test",
            TenantMailRecipientResolver.resolve_contact_email(tenant),
        )

    def test_resolve_contact_recipient_uses_display_name_when_branding_exists(self) -> None:
        """ Build one tenant-facing recipient with the preferred business display name. """
        tenant = TenantModel(
            name="GEA Trader Legal",
            slug="gea-trader-legal",
            business_email="hello@gea-trader.test",
        )
        branding = TenantBrandingModel(
            tenant=tenant,
            display_name="GEA Trader",
        )
        tenant._state.fields_cache["branding"] = branding

        recipient = TenantMailRecipientResolver.resolve_contact_recipient(tenant)

        self.assertIsNotNone(recipient)
        self.assertEqual("hello@gea-trader.test", recipient.email)
        self.assertEqual("GEA Trader", recipient.name)
