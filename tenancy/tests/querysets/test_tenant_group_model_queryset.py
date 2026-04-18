"""QuerySet tests for tenant-group filters."""

from django.contrib.auth.models import Group
from core.testing.base import LoggedTestCase
from tenancy.models import TenantGroupModel, TenantModel


class TestTenantGroupModelQuerySet(LoggedTestCase):
    """Verify reusable tenant-group queryset helpers."""

    def setUp(self) -> None:
        """Create reusable tenant-group bindings for queryset tests."""
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        self.inactive_tenant = TenantModel.objects.create(
            name="Inactive Center",
            slug="inactive-center",
            is_active=False,
        )
        self.sales_group = Group.objects.create(name="Sales")
        self.accounts_group = Group.objects.create(name="Accounts")
        self.inactive_group = Group.objects.create(name="Inactive Tenant Group")
        self.sales_binding = TenantGroupModel.objects.create(tenant=self.tenant, group=self.sales_group)
        self.accounts_binding = TenantGroupModel.objects.create(tenant=self.other_tenant, group=self.accounts_group)
        self.inactive_binding = TenantGroupModel.objects.create(tenant=self.inactive_tenant, group=self.inactive_group)

    def test_for_tenant_filters_bindings_by_tenant(self) -> None:
        """Verify bindings can be filtered by tenant."""
        self.assertEqual([self.sales_binding], list(TenantGroupModel.objects.for_tenant(self.tenant)))

    def test_for_group_filters_bindings_by_group(self) -> None:
        """Verify bindings can be filtered by Django group."""
        self.assertEqual([self.sales_binding], list(TenantGroupModel.objects.for_group(self.sales_group)))

    def test_for_active_tenant_filters_out_bindings_for_inactive_tenants(self) -> None:
        """Verify bindings can be narrowed to active tenants only."""
        self.assertEqual(
            [self.sales_binding, self.accounts_binding],
            list(TenantGroupModel.objects.for_active_tenant().order_by("id")),
        )
        self.assertNotIn(self.inactive_binding, list(TenantGroupModel.objects.for_active_tenant()))

    def test_with_group_selects_related_group(self) -> None:
        """Verify bindings can eager-load the related Django group."""
        queryset = TenantGroupModel.objects.with_group()

        self.assertIn("group", queryset.query.select_related)

    def test_with_tenant_selects_related_tenant(self) -> None:
        """Verify bindings can eager-load the related tenant."""
        queryset = TenantGroupModel.objects.with_tenant()

        self.assertIn("tenant", queryset.query.select_related)
