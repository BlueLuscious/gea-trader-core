""" Manager tests for tenant membership access helpers. """

from core.testing.base import LoggedTestCase
from accounts.models import UserModel
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestTenantMembershipModelManager(LoggedTestCase):
    """ Verify the tenant membership manager exposes the expected shortcuts. """

    def setUp(self) -> None:
        """ Create reusable memberships for manager tests. """
        self.user = UserModel.objects.create_user(username="lucio", password="test-pass")
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.owner_membership = TenantMembershipModel.objects.create(
            tenant=self.tenant,
            user=self.user,
            role=TenantRole.OWNER,
            is_active=True,
            is_primary=True,
        )

    def test_active_returns_only_active_memberships(self) -> None:
        """ Verify the membership manager exposes the active queryset shortcut. """
        self.assertEqual([self.owner_membership], list(TenantMembershipModel.objects.active()))

    def test_for_user_returns_related_memberships(self) -> None:
        """ Verify the membership manager exposes the user-scoped queryset shortcut. """
        self.assertEqual([self.owner_membership], list(TenantMembershipModel.objects.for_user(self.user)))

    def test_for_tenant_returns_related_memberships(self) -> None:
        """ Verify the membership manager exposes the tenant-scoped queryset shortcut. """
        self.assertEqual([self.owner_membership], list(TenantMembershipModel.objects.for_tenant(self.tenant)))

    def test_primary_returns_primary_memberships(self) -> None:
        """ Verify the membership manager exposes the primary queryset shortcut. """
        self.assertEqual([self.owner_membership], list(TenantMembershipModel.objects.primary()))

    def test_owners_returns_owner_memberships(self) -> None:
        """ Verify the membership manager exposes the owner-role queryset shortcut. """
        self.assertEqual([self.owner_membership], list(TenantMembershipModel.objects.owners()))

    def test_for_user_active_tenants_returns_active_memberships_for_active_tenants(self) -> None:
        """ Verify the membership manager exposes the user active-tenant shortcut. """
        active_secondary_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        inactive_tenant = TenantModel.objects.create(
            name="Inactive Center",
            slug="inactive-center",
            is_active=False,
        )
        active_secondary_membership = TenantMembershipModel.objects.create(
            tenant=active_secondary_tenant,
            user=self.user,
            role=TenantRole.MASTER,
            is_active=True,
        )
        TenantMembershipModel.objects.create(
            tenant=inactive_tenant,
            user=self.user,
            role=TenantRole.MASTER,
            is_active=True,
        )

        self.assertEqual(
            [self.owner_membership, active_secondary_membership],
            list(TenantMembershipModel.objects.for_user_active_tenants(self.user).order_by("id")),
        )

    def test_ordered_for_active_tenant_resolution_returns_primary_first(self) -> None:
        """ Verify the membership manager exposes the active-tenant ordering shortcut. """
        other_tenant = TenantModel.objects.create(name="Alpha Center", slug="alpha-center")
        secondary_membership = TenantMembershipModel.objects.create(
            tenant=other_tenant,
            user=self.user,
            role=TenantRole.MASTER,
            is_active=True,
            is_primary=False,
        )

        self.assertEqual(
            [self.owner_membership, secondary_membership],
            list(
                TenantMembershipModel.objects.for_user(self.user).ordered_for_active_tenant_resolution()
            ),
        )
