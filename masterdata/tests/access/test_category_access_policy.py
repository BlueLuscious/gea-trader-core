""" Access policy tests for tenant-scoped category flows. """

from django.contrib.auth.models import Permission
from django.test import RequestFactory
from accounts.models import UserModel
from core.testing.base import LoggedTestCase
from masterdata.access import CategoryAccessPolicy
from masterdata.models import CategoryModel
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestCategoryAccessPolicy(LoggedTestCase):
    """ Verify category access stays scoped to the active tenant. """

    def setUp(self) -> None:
        """ Create reusable request factory, tenants, actor, and category fixtures. """
        self.request_factory = RequestFactory()
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        self.operator = UserModel.objects.create_user(
            username="category-operator",
            password="test-pass",
            is_active=True,
            is_staff=True,
        )
        self.outsider = UserModel.objects.create_user(
            username="category-outsider",
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
                    "view_categorymodel",
                    "add_categorymodel",
                    "change_categorymodel",
                    "delete_categorymodel",
                )
            )
        )
        self.in_scope_category = CategoryModel.objects.create(
            tenant=self.tenant,
            name="Industrial",
            slug="industrial",
        )
        self.out_of_scope_category = CategoryModel.objects.create(
            tenant=self.other_tenant,
            name="Legacy",
            slug="legacy",
        )

    def build_request(self, user: UserModel, tenant: TenantModel | None) -> object:
        """ Build one owner-admin style request for one user and tenant context.

        Args:
            user: Authenticated actor.
            tenant: Active tenant in scope.

        Returns:
            object: Request object carrying the actor and tenant.
        """
        request = self.request_factory.get("/owner-admin/masterdata/categorymodel/")
        request.user = user
        request.tenant = tenant
        return request

    def test_can_access_categories_requires_membership_and_view_permission(self) -> None:
        """ Verify category access depends on active-tenant membership plus view permission. """
        member_request = self.build_request(self.operator, self.tenant)
        outsider_request = self.build_request(self.outsider, self.tenant)

        self.assertTrue(CategoryAccessPolicy.can_access_categories(member_request))
        self.assertFalse(CategoryAccessPolicy.can_access_categories(outsider_request))

    def test_category_permissions_reject_objects_from_other_tenants(self) -> None:
        """ Verify category object permissions stay scoped to the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(CategoryAccessPolicy.can_view_category(request, self.in_scope_category))
        self.assertTrue(CategoryAccessPolicy.can_change_category(request, self.in_scope_category))
        self.assertTrue(CategoryAccessPolicy.can_delete_category(request, self.in_scope_category))
        self.assertFalse(CategoryAccessPolicy.can_view_category(request, self.out_of_scope_category))
        self.assertFalse(CategoryAccessPolicy.can_change_category(request, self.out_of_scope_category))
        self.assertFalse(CategoryAccessPolicy.can_delete_category(request, self.out_of_scope_category))

    def test_add_category_requires_membership_and_permission(self) -> None:
        """ Verify category creation stays blocked without active-tenant access. """
        member_request = self.build_request(self.operator, self.tenant)
        outsider_request = self.build_request(self.outsider, self.tenant)

        self.assertTrue(CategoryAccessPolicy.can_add_category(member_request))
        self.assertFalse(CategoryAccessPolicy.can_add_category(outsider_request))
