from django.core.exceptions import ValidationError
from django.utils.translation import override
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

    def test_category_child_names_can_repeat_when_slugs_are_different(self) -> None:
        """ Verify similarly named child categories can live under different roots. """
        tenant = self._create_tenant("duplicate-category-names")
        first_root = CategoryModel.objects.create(tenant=tenant, name="Industrial", slug="industrial")
        second_root = CategoryModel.objects.create(tenant=tenant, name="Agriculture", slug="agriculture")
        first_child = CategoryModel.objects.create(
            tenant=tenant,
            name="Hydraulic Oils",
            slug="industrial-hydraulic-oils",
            parent=first_root,
        )
        second_child = CategoryModel.objects.create(
            tenant=tenant,
            name="Hydraulic Oils",
            slug="agriculture-hydraulic-oils",
            parent=second_root,
        )

        self.assertEqual(first_child.name, second_child.name)
        self.assertEqual(first_root.children.get(), first_child)
        self.assertEqual(second_root.children.get(), second_child)

    def test_category_slug_must_be_unique_inside_one_tenant(self) -> None:
        """ Verify duplicate category slugs are rejected inside one tenant. """
        tenant = self._create_tenant("duplicate-category-slugs")
        first_root = CategoryModel.objects.create(tenant=tenant, name="Industrial", slug="industrial")
        second_root = CategoryModel.objects.create(tenant=tenant, name="Agriculture", slug="agriculture")
        CategoryModel.objects.create(
            tenant=tenant,
            name="Hydraulic Oils",
            slug="hydraulic-oils",
            parent=first_root,
        )
        duplicated_slug_category = CategoryModel(
            tenant=tenant,
            name="Hydraulic Oils",
            slug="hydraulic-oils",
            parent=second_root,
        )

        with self.assertRaises(ValidationError):
            duplicated_slug_category.full_clean()

    def test_category_slug_can_repeat_across_different_tenants(self) -> None:
        """ Verify the category slug uniqueness boundary is scoped per tenant. """
        first_tenant = self._create_tenant("first-duplicate-slug-tenant")
        second_tenant = self._create_tenant("second-duplicate-slug-tenant")
        first_category = CategoryModel.objects.create(
            tenant=first_tenant,
            name="Hydraulic Oils",
            slug="hydraulic-oils",
        )
        second_category = CategoryModel(
            tenant=second_tenant,
            name="Hydraulic Oils",
            slug="hydraulic-oils",
        )

        second_category.full_clean()
        second_category.save()

        self.assertEqual(first_category.slug, second_category.slug)

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

    def test_model_field_metadata_uses_friendly_translatable_copy(self) -> None:
        """ Verify masterdata model fields expose user-friendly labels and help texts. """
        brand_name_field = BrandModel._meta.get_field("name")
        brand_slug_field = BrandModel._meta.get_field("slug")
        category_name_field = CategoryModel._meta.get_field("name")
        category_banner_field = CategoryModel._meta.get_field("banner")
        category_parent_field = CategoryModel._meta.get_field("parent")
        category_sort_order_field = CategoryModel._meta.get_field("sort_order")
        category_is_featured_field = CategoryModel._meta.get_field("is_featured")

        with override("en"):
            self.assertEqual("Brand name", str(brand_name_field.verbose_name))
            self.assertEqual(
                "Usually created from the brand name. Adjust it only when you need a custom URL.",
                str(brand_slug_field.help_text),
            )
            self.assertEqual("Category name", str(category_name_field.verbose_name))
            self.assertEqual("Banner", str(category_banner_field.verbose_name))
            self.assertEqual("Parent category", str(category_parent_field.verbose_name))
            self.assertEqual("Display order", str(category_sort_order_field.verbose_name))
            self.assertEqual("Featured on the site", str(category_is_featured_field.verbose_name))
