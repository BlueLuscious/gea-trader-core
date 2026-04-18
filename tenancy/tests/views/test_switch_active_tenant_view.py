""" Tests for explicit active-tenant switching. """

from unittest.mock import patch
from django.urls import reverse
from accounts.models import UserModel
from core.testing.base import LoggedTestCase
from tenancy.models import TenantMembershipModel, TenantModel


class TestSwitchActiveTenantView(LoggedTestCase):
    """ Verify authenticated users can switch their active tenant safely. """

    def setUp(self) -> None:
        """ Create reusable users and tenants for switch-view coverage. """
        self.user = UserModel.objects.create_user(username="lucio", password="test-pass")
        self.primary_tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.secondary_tenant = TenantModel.objects.create(name="North Center", slug="north-center")
        self.foreign_tenant = TenantModel.objects.create(name="Foreign Center", slug="foreign-center")

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

        self.client.force_login(self.user)

    def test_switch_active_tenant_view_updates_the_session_for_valid_memberships(self) -> None:
        """ Verify the switch view stores the selected tenant in session for valid memberships. """
        with patch("tenancy.switching.active_tenant_switcher.logger.info") as switcher_logger_mock:
            response = self.client.get(
                reverse("switch-active-tenant", kwargs={"tenant_id": self.secondary_tenant.pk})
            )

        self.assertEqual(302, response.status_code)
        self.assertEqual("/owner-admin/", response.url)
        self.assertEqual(str(self.secondary_tenant.pk), self.client.session["active_tenant_id"])
        switcher_logger_mock.assert_called_once()

    def test_switch_active_tenant_view_redirects_to_safe_next_url(self) -> None:
        """ Verify the switch view honors one safe next URL after updating the session. """
        with patch("tenancy.views.switch_active_tenant_view.logger.info") as view_logger_mock:
            response = self.client.get(
                reverse("switch-active-tenant", kwargs={"tenant_id": self.secondary_tenant.pk}),
                {"next": "/owner-admin/"},
            )

        self.assertEqual(302, response.status_code)
        self.assertEqual("/owner-admin/", response.url)
        view_logger_mock.assert_called_once()

    def test_switch_active_tenant_view_rejects_tenants_without_membership(self) -> None:
        """ Verify the switch view returns forbidden when the user does not belong to the tenant. """
        with patch("tenancy.switching.active_tenant_switcher.logger.warning") as switcher_logger_mock:
            response = self.client.get(
                reverse("switch-active-tenant", kwargs={"tenant_id": self.foreign_tenant.pk})
            )

        self.assertEqual(403, response.status_code)
        switcher_logger_mock.assert_called_once()
