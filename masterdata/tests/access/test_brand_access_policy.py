""" Access policy tests for tenant-scoped brand flows. """

from django.contrib.auth.models import Permission
from django.test import RequestFactory
from accounts.models import UserModel
from core.testing.base import LoggedTestCase
from masterdata.access import BrandAccessPolicy
from masterdata.models import BrandModel
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestBrandAccessPolicy(LoggedTestCase):
    """ Verify brand access stays scoped to the active tenant. """

    def setUp(self) -> None:
        """ Create reusable request factory, tenants, actor, and brand fixtures. """
        self.request_factory = RequestFactory()
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        self.operator = UserModel.objects.create_user(
            username="brand-operator",
            password="test-pass",
            is_active=True,
            is_staff=True,
        )
        self.outsider = UserModel.objects.create_user(
            username="brand-outsider",
            password="test-pass",
            is_active=True,
            is_staff=True,
        )
        TenantMembershipModel.objects.create(
            tenant=self.tenant,
            user=self.operator,
            role=TenantRole.OPERATOR,
            is_active=True,
            is_primary=True,
        )
        self.operator.user_permissions.set(
            Permission.objects.filter(
                codename__in=(
                    "view_brandmodel",
                    "add_brandmodel",
                    "change_brandmodel",
                    "delete_brandmodel",
                )
            )
        )
        self.in_scope_brand = BrandModel.objects.create(
            tenant=self.tenant,
            name="GEA",
            slug="gea",
        )
        self.out_of_scope_brand = BrandModel.objects.create(
            tenant=self.other_tenant,
            name="Other",
            slug="other",
        )

    def build_request(self, user: UserModel, tenant: TenantModel | None) -> object:
        """ Build one owner-admin style request for one user and tenant context.

        Args:
            user: Authenticated actor.
            tenant: Active tenant in scope.

        Returns:
            object: Request object carrying the actor and tenant.
        """
        request = self.request_factory.get("/owner-admin/masterdata/brandmodel/")
        request.user = user
        request.tenant = tenant
        return request

    def test_can_access_brands_requires_membership_and_view_permission(self) -> None:
        """ Verify brand access depends on active-tenant membership plus view permission. """
        member_request = self.build_request(self.operator, self.tenant)
        outsider_request = self.build_request(self.outsider, self.tenant)

        self.assertTrue(BrandAccessPolicy.can_access_brands(member_request))
        self.assertFalse(BrandAccessPolicy.can_access_brands(outsider_request))

    def test_brand_permissions_reject_objects_from_other_tenants(self) -> None:
        """ Verify brand object permissions stay scoped to the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(BrandAccessPolicy.can_view_brand(request, self.in_scope_brand))
        self.assertTrue(BrandAccessPolicy.can_change_brand(request, self.in_scope_brand))
        self.assertTrue(BrandAccessPolicy.can_delete_brand(request, self.in_scope_brand))
        self.assertFalse(BrandAccessPolicy.can_view_brand(request, self.out_of_scope_brand))
        self.assertFalse(BrandAccessPolicy.can_change_brand(request, self.out_of_scope_brand))
        self.assertFalse(BrandAccessPolicy.can_delete_brand(request, self.out_of_scope_brand))

    def test_add_brand_requires_membership_and_permission(self) -> None:
        """ Verify brand creation stays blocked without active-tenant access. """
        member_request = self.build_request(self.operator, self.tenant)
        outsider_request = self.build_request(self.outsider, self.tenant)

        self.assertTrue(BrandAccessPolicy.can_add_brand(member_request))
        self.assertFalse(BrandAccessPolicy.can_add_brand(outsider_request))
