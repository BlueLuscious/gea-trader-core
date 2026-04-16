from django.core.exceptions import ValidationError
from core.testing.base import LoggedTestCase
from masterdata.models import BrandModel, CategoryModel
from tenancy.models import TenantModel


class TestMasterdataModel(LoggedTestCase):
    """ Cover masterdata model behavior. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for masterdata ownership tests.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_brand_and_category_string_representation(self) -> None:
        """ Verify brand and category string representations. """
        tenant = self._create_tenant("masterdata-strings")
        brand = BrandModel.objects.create(tenant=tenant, name="GEA", slug="gea")
        category = CategoryModel.objects.create(tenant=tenant, name="Lubricacion", slug="lubricacion")

        self.assertEqual(str(brand), "GEA")
        self.assertEqual(str(category), "Lubricacion")

    def test_category_parent_relationship(self) -> None:
        """ Verify category parent relationship persists correctly. """
        tenant = self._create_tenant("masterdata-parent")
        parent = CategoryModel.objects.create(tenant=tenant, name="Industrial", slug="industrial")
        child = CategoryModel.objects.create(tenant=tenant, name="Lubricacion", slug="lubricacion", parent=parent)

        self.assertEqual(child.parent, parent)
        self.assertEqual(parent.children.get(), child)

    def test_category_parent_must_belong_to_the_same_tenant(self) -> None:
        """ Reject category trees that try to cross tenant boundaries. """
        first_tenant = self._create_tenant("north-masterdata")
        second_tenant = self._create_tenant("south-masterdata")
        parent = CategoryModel.objects.create(tenant=first_tenant, name="Industrial", slug="industrial")
        child = CategoryModel(tenant=second_tenant, name="Lubricacion", slug="lubricacion", parent=parent)

        with self.assertRaises(ValidationError):
            child.save()

    def test_category_cannot_parent_itself(self) -> None:
        """ Reject category rows that try to point to themselves as parent. """
        tenant = self._create_tenant("self-parent-masterdata")
        category = CategoryModel.objects.create(tenant=tenant, name="Industrial", slug="industrial")
        category.parent = category

        with self.assertRaises(ValidationError):
            category.save()

    def test_category_hierarchy_cannot_contain_cycles(self) -> None:
        """ Reject category trees that try to loop back into one ancestor. """
        tenant = self._create_tenant("cycle-masterdata")
        root = CategoryModel.objects.create(tenant=tenant, name="Root", slug="root")
        child = CategoryModel.objects.create(tenant=tenant, name="Child", slug="child", parent=root)
        grandchild = CategoryModel.objects.create(tenant=tenant, name="Grandchild", slug="grandchild", parent=child)
        root.parent = grandchild

        with self.assertRaises(ValidationError):
            root.save()
