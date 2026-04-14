""" Tests for the catalog access policy. """

from django.contrib.auth.models import Permission
from django.test import RequestFactory
from accounts.models import UserModel
from catalog.access import CatalogAccessPolicy
from catalog.models import ProductModel
from core.testing.base import LoggedTestCase
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestCatalogAccessPolicy(LoggedTestCase):
    """ Verify tenant-scoped catalog access stays aligned with memberships and permissions. """

    def setUp(self) -> None:
        """ Create reusable requests, tenants, users, and product fixtures. """
        self.request_factory = RequestFactory()
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        self.operator = UserModel.objects.create_user(
            username="catalog-operator",
            password="test-pass",
            is_active=True,
            is_staff=True,
        )
        self.no_permission_user = UserModel.objects.create_user(
            username="catalog-no-permission",
            password="test-pass",
            is_active=True,
            is_staff=True,
        )
        self.outsider = UserModel.objects.create_user(
            username="catalog-outsider",
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
        TenantMembershipModel.objects.create(
            tenant=self.tenant,
            user=self.no_permission_user,
            role=TenantRole.OPERATOR,
            is_active=True,
            is_primary=True,
        )
        self.operator.user_permissions.set(
            Permission.objects.filter(
                codename__in=(
                    "view_productmodel",
                    "add_productmodel",
                    "change_productmodel",
                    "delete_productmodel",
                )
            )
        )
        self.product = ProductModel.objects.create(tenant=self.tenant, name="Pump", slug="pump")
        self.other_product = ProductModel.objects.create(tenant=self.other_tenant, name="Filter", slug="filter")

    def build_request(self, user: UserModel, tenant: TenantModel | None) -> object:
        """ Build one owner-admin request for one user and tenant context.

        Args:
            user: Authenticated actor.
            tenant: Active tenant in scope.

        Returns:
            object: Request carrying the actor and tenant context.
        """
        request = self.request_factory.get("/owner-admin/catalog/productmodel/")
        request.user = user
        request.tenant = tenant
        return request

    def test_can_access_catalog_returns_true_for_active_tenant_members_with_view_permission(self) -> None:
        """ Allow catalog access for active tenant members that hold the product view permission. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(CatalogAccessPolicy.can_access_catalog(request))

    def test_can_access_catalog_returns_false_without_the_view_permission(self) -> None:
        """ Reject catalog access when the actor lacks the base product view permission. """
        request = self.build_request(self.no_permission_user, self.tenant)

        self.assertFalse(CatalogAccessPolicy.can_access_catalog(request))

    def test_can_access_catalog_returns_false_without_an_active_tenant_context(self) -> None:
        """ Reject catalog access when the request has no active tenant. """
        request = self.build_request(self.operator, None)

        self.assertFalse(CatalogAccessPolicy.can_access_catalog(request))

    def test_can_view_product_returns_false_for_products_outside_the_active_tenant(self) -> None:
        """ Hide products that do not belong to the request tenant even when permissions exist. """
        request = self.build_request(self.operator, self.tenant)

        self.assertFalse(CatalogAccessPolicy.can_view_product(request, self.other_product))

    def test_can_change_product_returns_true_for_in_scope_products_with_change_permission(self) -> None:
        """ Allow editing products that belong to the active tenant when the actor may change products. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(CatalogAccessPolicy.can_change_product(request, self.product))

    def test_can_add_product_returns_false_for_non_members_even_when_permissions_exist(self) -> None:
        """ Reject product creation when the actor does not belong to the active tenant. """
        self.outsider.user_permissions.set(
            Permission.objects.filter(codename__in=("view_productmodel", "add_productmodel"))
        )
        request = self.build_request(self.outsider, self.tenant)

        self.assertFalse(CatalogAccessPolicy.can_add_product(request))
