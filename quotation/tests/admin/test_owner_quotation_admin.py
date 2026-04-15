""" Owner admin tests for tenant-scoped quotation flows. """

from decimal import Decimal
from django.contrib.auth.models import Permission
from django.test import RequestFactory
from accounts.models import UserModel
from catalog.models import ProductModel, ProductVariantModel
from core.adminsites.site_instances import owner_admin_site
from core.testing.base import LoggedTestCase
from quotation.admin.owner.quote_item_model_inline import QuoteItemModelInline
from quotation.admin.owner.quote_model_admin import QuoteModelAdmin
from quotation.models import QuoteModel
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestOwnerQuotationAdmin(LoggedTestCase):
    """ Verify the owner quotation admin stays scoped to the active tenant. """

    def setUp(self) -> None:
        """ Create reusable request factory, tenant, operator, and quote fixtures. """
        self.request_factory = RequestFactory()
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        self.operator = UserModel.objects.create_user(
            username="quotation-operator",
            password="test-pass",
            is_active=True,
            is_staff=True,
        )
        self.outsider = UserModel.objects.create_user(
            username="quotation-outsider",
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
                codename__in=("view_quotemodel", "add_quotemodel", "change_quotemodel")
            )
        )
        self.in_scope_quote = QuoteModel.objects.create(
            tenant=self.tenant,
            customer_email="north@example.com",
        )
        self.out_of_scope_quote = QuoteModel.objects.create(
            tenant=self.other_tenant,
            customer_email="south@example.com",
        )
        self.in_scope_product = ProductModel.objects.create(
            tenant=self.tenant,
            name="Pump",
            slug="pump",
            sku_base="PUMP",
        )
        self.out_of_scope_product = ProductModel.objects.create(
            tenant=self.other_tenant,
            name="Filter",
            slug="filter",
            sku_base="FILTER",
        )
        self.in_scope_variant = ProductVariantModel.objects.create(
            product=self.in_scope_product,
            sku="PUMP-001",
            price=Decimal("42.50"),
        )
        ProductVariantModel.objects.create(
            product=self.out_of_scope_product,
            sku="FILTER-001",
        )
        self.admin = QuoteModelAdmin(QuoteModel, owner_admin_site)

    def build_request(self, user: UserModel, tenant: TenantModel | None) -> object:
        """ Build one owner-admin request for one user and tenant context.

        Args:
            user: Authenticated actor.
            tenant: Active tenant in scope.

        Returns:
            object: Request object carrying the actor and tenant.
        """
        request = self.request_factory.get("/owner-admin/quotation/quotemodel/")
        request.user = user
        request.tenant = tenant
        return request

    def test_get_queryset_is_scoped_to_the_active_tenant(self) -> None:
        """ Verify the owner quote queryset only returns quotes from the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        queryset = self.admin.get_queryset(request)

        self.assertEqual([self.in_scope_quote], list(queryset))

    def test_save_model_assigns_the_active_tenant_on_create(self) -> None:
        """ Verify owner-created quotes inherit the active tenant automatically. """
        request = self.build_request(self.operator, self.tenant)
        quote = QuoteModel(customer_name="Manual quote", customer_email="manual@example.com")
        form = QuoteModelAdmin.form(instance=quote)

        self.admin.save_model(request, quote, form, change=False)

        self.assertEqual(self.tenant, quote.tenant)

    def test_view_and_change_permissions_reject_quotes_from_other_tenants(self) -> None:
        """ Verify quote object permissions stay scoped to the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(self.admin.has_view_permission(request, self.in_scope_quote))
        self.assertTrue(self.admin.has_change_permission(request, self.in_scope_quote))
        self.assertFalse(self.admin.has_view_permission(request, self.out_of_scope_quote))
        self.assertFalse(self.admin.has_change_permission(request, self.out_of_scope_quote))

    def test_module_and_add_permissions_require_quotation_access(self) -> None:
        """ Verify quotation module and add access stay blocked without tenant membership. """
        member_request = self.build_request(self.operator, self.tenant)
        outsider_request = self.build_request(self.outsider, self.tenant)

        self.assertTrue(self.admin.has_module_permission(member_request))
        self.assertTrue(self.admin.has_add_permission(member_request))
        self.assertFalse(self.admin.has_module_permission(outsider_request))
        self.assertFalse(self.admin.has_add_permission(outsider_request))

    def test_quote_item_inline_limits_catalog_choices_to_the_active_tenant(self) -> None:
        """ Verify add-time quote item choices expose only products and variants from the active tenant. """
        inline = QuoteItemModelInline(QuoteModel, owner_admin_site)
        request = self.build_request(self.operator, self.tenant)
        request.method = "POST"
        formset_class = inline.get_formset(request, obj=None)
        formset = formset_class(instance=QuoteModel(tenant=self.tenant))
        empty_form = formset.empty_form

        self.assertEqual([self.in_scope_product], list(empty_form.fields["product"].queryset))
        self.assertEqual([self.in_scope_variant], list(empty_form.fields["variant"].queryset))
