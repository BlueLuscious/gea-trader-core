from core.testing.base import LoggedTestCase
from masterdata.models import BrandModel, CategoryModel


class TestMasterdataModel(LoggedTestCase):
    """ Cover masterdata model behavior. """

    def test_brand_and_category_string_representation(self) -> None:
        """ Verify brand and category string representations. """
        brand = BrandModel.objects.create(name="GEA", slug="gea")
        category = CategoryModel.objects.create(name="Lubricacion", slug="lubricacion")

        self.assertEqual(str(brand), "GEA")
        self.assertEqual(str(category), "Lubricacion")

    def test_category_parent_relationship(self) -> None:
        """ Verify category parent relationship persists correctly. """
        parent = CategoryModel.objects.create(name="Industrial", slug="industrial")
        child = CategoryModel.objects.create(name="Lubricacion", slug="lubricacion", parent=parent)

        self.assertEqual(child.parent, parent)
        self.assertEqual(parent.children.get(), child)
