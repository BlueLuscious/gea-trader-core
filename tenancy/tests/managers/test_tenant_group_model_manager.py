"""Manager tests for tenant-group access helpers."""

from django.contrib.auth.models import Group
from core.testing.base import LoggedTestCase
from tenancy.models import TenantGroupModel, TenantModel


class TestTenantGroupModelManager(LoggedTestCase):
    """Verify the tenant-group manager exposes the expected shortcuts."""

    def setUp(self) -> None:
        """Create reusable tenant-group bindings for manager tests."""
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.sales_group = Group.objects.create(name="Sales")
        self.binding = TenantGroupModel.objects.create(tenant=self.tenant, group=self.sales_group)

    def test_for_tenant_returns_related_bindings(self) -> None:
        """Verify the manager exposes the tenant-scoped queryset shortcut."""
        self.assertEqual([self.binding], list(TenantGroupModel.objects.for_tenant(self.tenant)))

    def test_for_group_returns_related_bindings(self) -> None:
        """Verify the manager exposes the group-scoped queryset shortcut."""
        self.assertEqual([self.binding], list(TenantGroupModel.objects.for_group(self.sales_group)))

    def test_for_active_tenant_returns_bindings_for_active_tenants_only(self) -> None:
        """Verify the manager exposes the active-tenant queryset shortcut."""
        inactive_tenant = TenantModel.objects.create(
            name="Inactive Center",
            slug="inactive-center",
            is_active=False,
        )
        inactive_group = Group.objects.create(name="Inactive")
        TenantGroupModel.objects.create(tenant=inactive_tenant, group=inactive_group)

        self.assertEqual([self.binding], list(TenantGroupModel.objects.for_active_tenant()))

    def test_with_group_selects_related_group(self) -> None:
        """Verify the manager exposes the eager-loading shortcut for groups."""
        self.assertIn("group", TenantGroupModel.objects.with_group().query.select_related)

    def test_with_tenant_selects_related_tenant(self) -> None:
        """Verify the manager exposes the eager-loading shortcut for tenants."""
        self.assertIn("tenant", TenantGroupModel.objects.with_tenant().query.select_related)
