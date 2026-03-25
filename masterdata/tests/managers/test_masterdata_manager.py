from core.testing.base import LoggedTestCase
from masterdata.models import BrandModel, CategoryModel


class TestMasterdataManager(LoggedTestCase):
    """ Cover masterdata manager helpers. """

    def test_brand_active_returns_only_active_brands(self) -> None:
        """ Verify the active brand manager helper filters inactive records. """
        active_brand = BrandModel.objects.create(name="GEA", slug="gea", is_active=True)
        BrandModel.objects.create(name="Old", slug="old", is_active=False)

        self.assertQuerySetEqual(BrandModel.objects.active(), [active_brand], transform=lambda instance: instance)

    def test_category_roots_returns_only_root_categories(self) -> None:
        """ Verify the roots category manager helper filters child categories. """
        root = CategoryModel.objects.create(name="Industrial", slug="industrial")
        CategoryModel.objects.create(name="Lubricacion", slug="lubricacion", parent=root)

        self.assertQuerySetEqual(CategoryModel.objects.roots(), [root], transform=lambda instance: instance)
