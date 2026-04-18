"""Model tests for tenant-group bindings."""

from django.contrib.auth.models import Group
from django.db import IntegrityError
from core.testing.base import LoggedTestCase
from tenancy.models import TenantGroupModel, TenantModel


class TestTenantGroupModel(LoggedTestCase):
    """Verify tenant-group persistence rules."""

    def setUp(self) -> None:
        """Create reusable tenant and auth groups for model tests."""
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        self.sales_group = Group.objects.create(name="Sales")

    def test_string_representation_prefers_tenant_and_group_name(self) -> None:
        """Verify the tenant-group string representation stays admin-friendly."""
        tenant_group = TenantGroupModel.objects.create(tenant=self.tenant, group=self.sales_group)

        self.assertIn("GEA Center", str(tenant_group))
        self.assertIn("Sales", str(tenant_group))

    def test_binding_enforces_one_group_per_tenant_scope(self) -> None:
        """Verify one Django group cannot be bound to multiple tenants."""
        TenantGroupModel.objects.create(tenant=self.tenant, group=self.sales_group)

        with self.assertRaises(IntegrityError):
            TenantGroupModel.objects.create(tenant=self.other_tenant, group=self.sales_group)
