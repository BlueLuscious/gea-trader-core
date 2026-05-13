""" Tests for quote owner-admin URL building. """

from django.test import override_settings
from core.testing.base import LoggedTestCase
from quotation.models import QuoteModel
from quotation.services import QuoteAdminUrlBuilder
from tenancy.models import TenantModel


class TestQuoteAdminUrlBuilder(LoggedTestCase):
    """ Verify quote admin links are built from the correct base URL. """

    @override_settings(BASE_URL="https://owner.geatrader.test")
    def test_build_prefers_base_url_setting(self) -> None:
        """ Verify BASE_URL is used before tenant website URL. """
        tenant = TenantModel.objects.create(
            name="GEA Oils",
            slug="gea-oils-url-base",
            website_url="https://public.geatrader.test",
        )
        quote = QuoteModel.objects.create(tenant=tenant, customer_name="Ada Lovelace")

        url = QuoteAdminUrlBuilder.build(quote=quote)

        self.assertEqual(
            url,
            f"https://owner.geatrader.test/owner-admin/quotation/quotemodel/{quote.id}/change/",
        )

    @override_settings(BASE_URL="")
    def test_build_uses_tenant_website_url_when_base_url_is_empty(self) -> None:
        """ Verify tenant website URL is the fallback absolute base. """
        tenant = TenantModel.objects.create(
            name="GEA Oils",
            slug="gea-oils-url-tenant",
            website_url="https://public.geatrader.test",
        )
        quote = QuoteModel.objects.create(tenant=tenant, customer_name="Ada Lovelace")

        url = QuoteAdminUrlBuilder.build(quote=quote)

        self.assertEqual(
            url,
            f"https://public.geatrader.test/owner-admin/quotation/quotemodel/{quote.id}/change/",
        )

    @override_settings(BASE_URL="")
    def test_build_returns_relative_path_without_any_base_url(self) -> None:
        """ Verify relative admin path remains available when no base exists. """
        tenant = TenantModel.objects.create(name="GEA Oils", slug="gea-oils-url-relative")
        quote = QuoteModel.objects.create(tenant=tenant, customer_name="Ada Lovelace")

        url = QuoteAdminUrlBuilder.build(quote=quote)

        self.assertEqual(url, f"/owner-admin/quotation/quotemodel/{quote.id}/change/")
