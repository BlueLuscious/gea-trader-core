""" Tests for owner-tenant branding resolution helpers. """

from django.test import RequestFactory
from unittest.mock import patch
from tenancy.models import TenantModel
from core.adminsites.services import OwnerTenantBrandingResolver
from core.testing.base import LoggedSimpleTestCase


class TestOwnerTenantBrandingResolver(LoggedSimpleTestCase):
    """ Verify tenant-branding helpers used by the owner admin site. """

    def setUp(self) -> None:
        """ Create the request factory used by the branding resolver tests. """
        self.request_factory = RequestFactory()

    @staticmethod
    def build_file(url: str) -> object:
        """ Build a minimal file-like object exposing one ``url`` attribute.

        Args:
            url: Asset URL returned by the fake file.

        Returns:
            object: File-like object used in branding resolver tests.
        """
        return type("BrandingFile", (), {"url": url})()

    def test_get_display_name_prefers_branding_display_name(self) -> None:
        """ Verify the branding resolver prefers the branding display name over the tenant name. """
        request = self.request_factory.get("/owner-admin/")
        request.tenant = TenantModel(name="GEA Lubricantes", slug="gea-lubricantes")
        request.tenant._state.fields_cache["branding"] = type("Branding", (), {"display_name": "GEA Trader"})()

        self.assertEqual("GEA Trader", OwnerTenantBrandingResolver.get_display_name(request))

    def test_get_display_name_falls_back_to_tenant_name(self) -> None:
        """ Verify the branding resolver falls back to the tenant name when no display name exists. """
        request = self.request_factory.get("/owner-admin/")
        request.tenant = TenantModel(name="GEA Lubricantes", slug="gea-lubricantes")

        self.assertEqual("GEA Lubricantes", OwnerTenantBrandingResolver.get_display_name(request))

    def test_get_branding_logs_when_the_request_has_no_active_tenant(self) -> None:
        """ Verify the branding resolver logs when the request has no active tenant context. """
        request = self.request_factory.get("/owner-admin/")
        request.tenant = None

        with patch("core.adminsites.services.owner_tenant_branding_resolver.logger.info") as logger_info_mock:
            branding = OwnerTenantBrandingResolver.get_branding(request)

        self.assertIsNone(branding)
        logger_info_mock.assert_called_once()

    def test_get_logo_and_icon_build_the_expected_themed_payload(self) -> None:
        """ Verify the branding resolver builds themed asset payloads for logos and icons. """
        request = self.request_factory.get("/owner-admin/")
        request.tenant = TenantModel(name="GEA Lubricantes", slug="gea-lubricantes")
        request.tenant._state.fields_cache["branding"] = type(
            "Branding",
            (),
            {
                "logo_light": self.build_file("/media/logo-light.png"),
                "logo_dark": self.build_file("/media/logo-dark.png"),
                "icon_light": self.build_file("/media/icon-light.png"),
                "icon_dark": self.build_file("/media/icon-dark.png"),
            },
        )()

        self.assertEqual(
            {"light": "/media/logo-light.png", "dark": "/media/logo-dark.png"},
            OwnerTenantBrandingResolver.get_logo(request),
        )
        self.assertEqual(
            {"light": "/media/icon-light.png", "dark": "/media/icon-dark.png"},
            OwnerTenantBrandingResolver.get_icon(request),
        )

    def test_get_favicons_return_unfold_ready_values(self) -> None:
        """ Verify the branding resolver returns favicon metadata. """
        request = self.request_factory.get("/owner-admin/")
        request.tenant = TenantModel(name="GEA Lubricantes", slug="gea-lubricantes")
        request.tenant._state.fields_cache["branding"] = type(
            "Branding",
            (),
            {
                "favicon_light": self.build_file("/media/favicon-light.png"),
                "favicon_dark": self.build_file("/media/favicon-dark.png"),
            },
        )()

        self.assertEqual(
            [
                {"href": "/media/favicon-light.png", "rel": "icon", "type": "image/png"},
                {"href": "/media/favicon-dark.png", "rel": "icon", "type": "image/png"},
            ],
            OwnerTenantBrandingResolver.get_favicons(request),
        )

    def test_get_favicons_returns_one_plain_entry_when_only_one_variant_exists(self) -> None:
        """ Verify the branding resolver keeps one plain favicon when only one variant exists. """
        request = self.request_factory.get("/owner-admin/")
        request.tenant = TenantModel(name="GEA Lubricantes", slug="gea-lubricantes")
        request.tenant._state.fields_cache["branding"] = type(
            "Branding",
            (),
            {
                "favicon_light": self.build_file("/media/favicon-light.png"),
                "favicon_dark": None,
            },
        )()

        self.assertEqual(
            [
                {"href": "/media/favicon-light.png", "rel": "icon", "type": "image/png"},
            ],
            OwnerTenantBrandingResolver.get_favicons(request),
        )
