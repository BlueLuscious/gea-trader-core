""" Tests for tenant-aware mail base context resolution. """

from core.mail import TenantMailContextResolver
from core.testing import LoggedSimpleTestCase
from tenancy.models import TenantBrandingModel, TenantModel
from tenancy.runtime import ActiveTenantContext


class TestTenantMailContextResolver(LoggedSimpleTestCase):
    """ Verify tenant-aware outbound mail context resolution. """

    def test_resolve_returns_neutral_values_when_no_tenant_is_active(self) -> None:
        """ Verify mail context stays neutral when no active tenant exists. """
        self.assertEqual(
            {
                "product_name": None,
                "support_email": None,
                "phone_number": None,
                "website_url": None,
            },
            TenantMailContextResolver.resolve(),
        )

    def test_resolve_prefers_branding_display_name_and_support_email(self) -> None:
        """ Verify branding display data and tenant support channels become the preferred mail context. """
        tenant = TenantModel(
            name="GEA Trader Legal",
            slug="gea-trader-legal",
            business_email="hello@gea-trader.test",
            support_email="support@gea-trader.test",
            phone_number="+54 11 5555 1234",
            website_url="https://gea-trader.test",
        )
        branding = TenantBrandingModel(
            tenant=tenant,
            display_name="GEA Trader",
        )
        tenant._state.fields_cache["branding"] = branding
        tenant_token = ActiveTenantContext.set(tenant)

        try:
            self.assertEqual(
                {
                    "product_name": "GEA Trader",
                    "support_email": "support@gea-trader.test",
                    "phone_number": "+54 11 5555 1234",
                    "website_url": "https://gea-trader.test",
                },
                TenantMailContextResolver.resolve(),
            )
        finally:
            ActiveTenantContext.reset(tenant_token)

    def test_resolve_falls_back_to_tenant_name_and_business_email(self) -> None:
        """ Verify mail context falls back to tenant name and business email when branding or support email are absent. """
        tenant = TenantModel(
            name="GEA Trader",
            slug="gea-trader",
            business_email="hello@gea-trader.test",
        )
        tenant_token = ActiveTenantContext.set(tenant)

        try:
            self.assertEqual(
                {
                    "product_name": "GEA Trader",
                    "support_email": "hello@gea-trader.test",
                    "phone_number": None,
                    "website_url": None,
                },
                TenantMailContextResolver.resolve(),
            )
        finally:
            ActiveTenantContext.reset(tenant_token)
