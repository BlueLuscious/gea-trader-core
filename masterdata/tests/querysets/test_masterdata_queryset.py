from core.testing.base import LoggedTestCase
from masterdata.models import BrandModel, CategoryModel


class TestMasterdataQuerySet(LoggedTestCase):
    """ Cover masterdata queryset helpers. """

    def test_brand_active_filters_inactive_rows(self) -> None:
        """ Verify BrandModelQuerySet.active filters by active flag. """
        active_brand = BrandModel.objects.create(name="GEA", slug="gea", is_active=True)
        BrandModel.objects.create(name="Legacy", slug="legacy", is_active=False)

        queryset = BrandModel.objects.get_queryset().active()

        self.assertQuerySetEqual(queryset, [active_brand], transform=lambda instance: instance)

    def test_category_active_roots_can_chain(self) -> None:
        """ Verify CategoryModelQuerySet supports active and root chaining. """
        active_root = CategoryModel.objects.create(name="Industrial", slug="industrial", is_active=True)
        inactive_root = CategoryModel.objects.create(name="Legacy", slug="legacy", is_active=False)
        CategoryModel.objects.create(name="Lubricacion", slug="lubricacion", parent=active_root, is_active=True)

        queryset = CategoryModel.objects.get_queryset().active().roots()

        self.assertQuerySetEqual(queryset, [active_root], transform=lambda instance: instance)
        self.assertNotIn(inactive_root, list(queryset))
