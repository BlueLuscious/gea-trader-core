""" Owner admin tests for tenant-scoped catalog flows. """

from django.contrib.auth.models import Permission
from django.test import RequestFactory
from accounts.models import UserModel
from catalog.admin.owner.product_model_admin import ProductModelAdmin
from catalog.models import ProductModel
from core.adminsites.site_instances import owner_admin_site
from core.testing.base import LoggedTestCase
from masterdata.models import BrandModel, CategoryModel
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestOwnerCatalogAdmin(LoggedTestCase):
    """ Verify the owner catalog admin stays scoped to the active tenant. """

    def setUp(self) -> None:
        """ Create reusable request factory, tenant, owner, and product fixtures. """
        self.request_factory = RequestFactory()
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        self.operator = UserModel.objects.create_user(
            username="catalog-operator",
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
        self.operator.user_permissions.set(
            Permission.objects.filter(
                codename__in=("view_productmodel", "add_productmodel", "change_productmodel")
            )
        )
        self.brand = BrandModel.objects.create(name="Brand", slug="brand")
        self.category = CategoryModel.objects.create(name="Category", slug="category")
        self.in_scope_product = ProductModel.objects.create(
            tenant=self.tenant,
            brand=self.brand,
            category=self.category,
            name="Pump",
            slug="pump",
        )
        self.out_of_scope_product = ProductModel.objects.create(
            tenant=self.other_tenant,
            brand=self.brand,
            category=self.category,
            name="Filter",
            slug="filter",
        )
        self.admin = ProductModelAdmin(ProductModel, owner_admin_site)

    def build_request(self, user: UserModel, tenant: TenantModel | None) -> object:
        """ Build one owner-admin request for one user and tenant context.

        Args:
            user: Authenticated actor.
            tenant: Active tenant in scope.

        Returns:
            object: Request object carrying the actor and tenant.
        """
        request = self.request_factory.get("/owner-admin/catalog/productmodel/")
        request.user = user
        request.tenant = tenant
        return request

    def test_get_queryset_is_scoped_to_the_active_tenant(self) -> None:
        """ Verify the owner product queryset only returns products from the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        queryset = self.admin.get_queryset(request)

        self.assertEqual([self.in_scope_product], list(queryset))

    def test_save_model_assigns_the_active_tenant_on_create(self) -> None:
        """ Verify owner-created products inherit the active tenant automatically. """
        request = self.build_request(self.operator, self.tenant)
        product = ProductModel(
            brand=self.brand,
            category=self.category,
            name="Valve",
            slug="valve",
        )
        form = ProductModelAdmin.form(instance=product)

        self.admin.save_model(request, product, form, change=False)

        self.assertEqual(self.tenant, product.tenant)

    def test_view_and_change_permissions_reject_products_from_other_tenants(self) -> None:
        """ Verify object permissions stay scoped to products owned by the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(self.admin.has_view_permission(request, self.in_scope_product))
        self.assertTrue(self.admin.has_change_permission(request, self.in_scope_product))
        self.assertFalse(self.admin.has_view_permission(request, self.out_of_scope_product))
        self.assertFalse(self.admin.has_change_permission(request, self.out_of_scope_product))

    def test_module_and_add_permissions_require_catalog_access(self) -> None:
        """ Verify catalog module and add access stay blocked without tenant membership. """
        member_request = self.build_request(self.operator, self.tenant)
        outsider_request = self.build_request(self.outsider, self.tenant)

        self.assertTrue(self.admin.has_module_permission(member_request))
        self.assertTrue(self.admin.has_add_permission(member_request))
        self.assertFalse(self.admin.has_module_permission(outsider_request))
        self.assertFalse(self.admin.has_add_permission(outsider_request))
