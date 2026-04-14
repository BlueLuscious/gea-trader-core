""" Access-policy tests for tenant-scoped quotation flows. """

from django.contrib.auth.models import Permission
from django.test import RequestFactory
from accounts.models import UserModel
from core.testing.base import LoggedTestCase
from quotation.access import QuotationAccessPolicy
from quotation.models import QuoteItemModel, QuoteModel
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestQuotationAccessPolicy(LoggedTestCase):
    """ Verify quotation access rules stay scoped to the active tenant. """

    def setUp(self) -> None:
        """ Create reusable tenants, users, memberships, and quote fixtures. """
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
                codename__in=(
                    "view_quotemodel",
                    "add_quotemodel",
                    "change_quotemodel",
                    "view_quoteitemmodel",
                )
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
        self.in_scope_item = QuoteItemModel.objects.create(
            quote=self.in_scope_quote,
            product_name_snapshot="Pump",
            quantity=1,
        )

    def build_request(self, user: UserModel, tenant: TenantModel | None) -> object:
        """ Build one request carrying one actor and one tenant context.

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

    def test_can_access_quotation_requires_membership_and_view_permission(self) -> None:
        """ Verify the quotation module requires active-tenant membership plus view permission. """
        member_request = self.build_request(self.operator, self.tenant)
        outsider_request = self.build_request(self.outsider, self.tenant)

        self.assertTrue(QuotationAccessPolicy.can_access_quotation(member_request))
        self.assertFalse(QuotationAccessPolicy.can_access_quotation(outsider_request))

    def test_can_add_quote_requires_add_permission(self) -> None:
        """ Verify quote creation requires the add permission in the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(QuotationAccessPolicy.can_add_quote(request))
        self.operator.user_permissions.remove(
            Permission.objects.get(codename="add_quotemodel", content_type__app_label="quotation")
        )
        self.operator = UserModel.objects.get(pk=self.operator.pk)
        request.user = self.operator

        self.assertFalse(QuotationAccessPolicy.can_add_quote(request))

    def test_can_view_and_change_quote_reject_cross_tenant_objects(self) -> None:
        """ Verify quote object access stays scoped to the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(QuotationAccessPolicy.can_view_quote(request, self.in_scope_quote))
        self.assertTrue(QuotationAccessPolicy.can_change_quote(request, self.in_scope_quote))
        self.assertFalse(QuotationAccessPolicy.can_view_quote(request, self.out_of_scope_quote))
        self.assertFalse(QuotationAccessPolicy.can_change_quote(request, self.out_of_scope_quote))

    def test_can_view_quote_item_uses_parent_quote_scope(self) -> None:
        """ Verify quote item access follows the tenant scope of the parent quote. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(QuotationAccessPolicy.can_view_quote_item(request, self.in_scope_item))
        self.assertFalse(QuotationAccessPolicy.can_view_quote_item(request, None))

    def test_can_access_quotation_returns_false_without_active_tenant(self) -> None:
        """ Verify quotation access is blocked when no active tenant exists on the request. """
        request = self.build_request(self.operator, None)

        self.assertFalse(QuotationAccessPolicy.can_access_quotation(request))
