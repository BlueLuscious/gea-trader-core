""" Tests for the owner admin tenant switcher dropdown. """

from urllib.parse import parse_qs, urlparse
from django.urls import resolve, reverse
from django.test import RequestFactory
from django.utils.translation import gettext as _
from unittest.mock import patch
from core.adminsites.site_instances import owner_admin_site
from core.testing.base import LoggedTestCase
from accounts.models import UserModel
from tenancy.models import TenantMembershipModel, TenantModel


class TestOwnerAdminSiteDropdown(LoggedTestCase):
    """ Verify the owner admin site exposes a tenant switcher for active memberships. """

    def setUp(self) -> None:
        """ Create reusable users and tenants for owner admin dropdown coverage. """
        self.request_factory = RequestFactory()
        self.user = UserModel.objects.create_user(
            username="owner-user",
            password="test-pass",
            is_staff=True,
        )
        self.primary_tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.secondary_tenant = TenantModel.objects.create(name="North Center", slug="north-center")

        TenantMembershipModel.objects.create(
            tenant=self.primary_tenant,
            user=self.user,
            is_primary=True,
        )
        TenantMembershipModel.objects.create(
            tenant=self.secondary_tenant,
            user=self.user,
            is_primary=False,
        )

    def test_get_site_dropdown_returns_active_tenant_switch_links(self) -> None:
        """ Verify the owner admin site exposes one switch link per active tenant membership. """
        request = self.request_factory.get("/owner-admin/")
        request.user = self.user
        request.tenant = self.primary_tenant

        with patch("core.adminsites.services.owner_tenant_dropdown_builder.logger.info") as logger_info_mock:
            dropdown_items = owner_admin_site.get_site_dropdown(request)

        self.assertEqual(2, len(dropdown_items))
        self.assertEqual(f"GEA Center ({_('Current')})", dropdown_items[0]["title"])
        self.assertIn(str(self.primary_tenant.pk), dropdown_items[0]["link"])
        self.assertEqual("check_circle", dropdown_items[0]["icon"])
        self.assertEqual("North Center", dropdown_items[1]["title"])
        self.assertIn(str(self.secondary_tenant.pk), dropdown_items[1]["link"])
        self.assertEqual("domain", dropdown_items[1]["icon"])
        logger_info_mock.assert_called_once()

    def test_get_site_dropdown_returns_empty_list_for_anonymous_like_users(self) -> None:
        """ Verify the owner admin dropdown stays empty when the user is not authenticated. """
        request = self.request_factory.get("/owner-admin/")
        request.user = type("AnonymousUserLike", (), {"is_authenticated": False})()
        request.tenant = None

        with patch("core.adminsites.services.owner_tenant_dropdown_builder.logger.info") as logger_info_mock:
            self.assertEqual([], owner_admin_site.get_site_dropdown(request))

        logger_info_mock.assert_called_once()

    def test_get_site_dropdown_rebuilds_tenant_change_next_for_target_tenant(self) -> None:
        """ Verify tenant settings links keep the business settings screen for the target tenant. """
        current_change_path = reverse(
            "owner_admin:tenancy_tenantmodel_change",
            kwargs={"object_id": str(self.primary_tenant.pk)},
        )
        request = self.request_factory.get(current_change_path)
        request.user = self.user
        request.tenant = self.primary_tenant
        request.resolver_match = resolve(current_change_path)

        dropdown_items = owner_admin_site.get_site_dropdown(request)
        secondary_link = dropdown_items[1]["link"]
        next_path = parse_qs(urlparse(secondary_link).query)["next"][0]

        self.assertEqual(
            reverse(
                "owner_admin:tenancy_tenantmodel_change",
                kwargs={"object_id": str(self.secondary_tenant.pk)},
            ),
            next_path,
        )

    def test_get_site_dropdown_falls_back_to_group_changelist_from_group_change_view(self) -> None:
        """ Verify non-tenant change screens fall back to the model changelist after switching. """
        current_group_change_path = reverse("owner_admin:auth_group_change", args=(1,))
        request = self.request_factory.get(current_group_change_path)
        request.user = self.user
        request.tenant = self.primary_tenant
        request.resolver_match = resolve(current_group_change_path)

        dropdown_items = owner_admin_site.get_site_dropdown(request)
        secondary_link = dropdown_items[1]["link"]
        next_path = parse_qs(urlparse(secondary_link).query)["next"][0]

        self.assertEqual(reverse("owner_admin:auth_group_changelist"), next_path)
