""" QuerySet tests for tenant membership filters. """

from core.testing.base import LoggedTestCase
from accounts.models import UserModel
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestTenantMembershipModelQuerySet(LoggedTestCase):
    """ Verify reusable tenant membership queryset helpers. """

    def setUp(self) -> None:
        """ Create reusable memberships for queryset tests. """
        self.user = UserModel.objects.create_user(username="lucio", password="test-pass")
        self.other_user = UserModel.objects.create_user(username="sofia", password="test-pass")
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        self.owner_membership = TenantMembershipModel.objects.create(
            tenant=self.tenant,
            user=self.user,
            role=TenantRole.OWNER,
            is_active=True,
            is_primary=True,
        )
        self.inactive_membership = TenantMembershipModel.objects.create(
            tenant=self.other_tenant,
            user=self.other_user,
            role=TenantRole.MASTER,
            is_active=False,
        )

    def test_active_filters_only_active_memberships(self) -> None:
        """ Verify active memberships exclude inactive rows. """
        self.assertEqual([self.owner_membership], list(TenantMembershipModel.objects.active()))

    def test_for_user_filters_memberships_by_user(self) -> None:
        """ Verify memberships can be filtered by user. """
        self.assertEqual([self.owner_membership], list(TenantMembershipModel.objects.for_user(self.user)))

    def test_for_tenant_filters_memberships_by_tenant(self) -> None:
        """ Verify memberships can be filtered by tenant. """
        self.assertEqual([self.owner_membership], list(TenantMembershipModel.objects.for_tenant(self.tenant)))

    def test_primary_filters_only_primary_memberships(self) -> None:
        """ Verify primary memberships filter excludes non-primary rows. """
        self.assertEqual([self.owner_membership], list(TenantMembershipModel.objects.primary()))

    def test_owners_filters_only_owner_memberships(self) -> None:
        """ Verify owner memberships filter excludes non-owner rows. """
        self.assertEqual([self.owner_membership], list(TenantMembershipModel.objects.owners()))

    def test_for_active_tenant_filters_out_memberships_for_inactive_tenants(self) -> None:
        """ Verify memberships can be filtered by active tenant state only. """
        inactive_tenant = TenantModel.objects.create(
            name="Inactive Center",
            slug="inactive-center",
            is_active=False,
        )
        active_tenant_membership = TenantMembershipModel.objects.create(
            tenant=self.other_tenant,
            user=self.user,
            role=TenantRole.MASTER,
            is_active=True,
        )
        inactive_tenant_membership = TenantMembershipModel.objects.create(
            tenant=inactive_tenant,
            user=self.user,
            role=TenantRole.MASTER,
            is_active=True,
        )

        self.assertEqual(
            [self.owner_membership, self.inactive_membership, active_tenant_membership],
            list(TenantMembershipModel.objects.for_active_tenant().order_by("id")),
        )
        self.assertNotIn(
            inactive_tenant_membership,
            list(TenantMembershipModel.objects.for_active_tenant()),
        )

    def test_for_user_active_tenants_combines_user_active_and_tenant_filters(self) -> None:
        """ Verify memberships can be narrowed to one user's active memberships on active tenants. """
        inactive_tenant = TenantModel.objects.create(
            name="Inactive Center",
            slug="inactive-center",
            is_active=False,
        )
        active_secondary_membership = TenantMembershipModel.objects.create(
            tenant=self.other_tenant,
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

    def test_ordered_for_active_tenant_resolution_sorts_primary_first_then_tenant_label(self) -> None:
        """ Verify active-tenant ordering remains deterministic. """
        third_tenant = TenantModel.objects.create(name="Alpha Center", slug="alpha-center")
        secondary_membership = TenantMembershipModel.objects.create(
            tenant=self.other_tenant,
            user=self.user,
            role=TenantRole.MASTER,
            is_active=True,
            is_primary=False,
        )
        third_membership = TenantMembershipModel.objects.create(
            tenant=third_tenant,
            user=self.user,
            role=TenantRole.MASTER,
            is_active=True,
            is_primary=False,
        )

        self.assertEqual(
            [self.owner_membership, third_membership, secondary_membership],
            list(
                TenantMembershipModel.objects.for_user(self.user).ordered_for_active_tenant_resolution()
            ),
        )
