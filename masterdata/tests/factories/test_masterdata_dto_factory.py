from core.testing.base import LoggedTestCase
from masterdata.dtos.factories import BrandModelDTOFactory, CategoryModelDTOFactory
from masterdata.models import BrandModel, CategoryModel


class TestMasterdataDTOFactory(LoggedTestCase):
    """ Cover masterdata DTO factories. """

    def test_brand_model_dto_factory_build_maps_fields(self) -> None:
        """ Verify BrandModelDTOFactory.build maps brand fields into a DTO. """
        brand = BrandModel.objects.create(name="GEA", slug="gea", description="Industrial")

        dto = BrandModelDTOFactory.build(brand)

        self.assertEqual(dto.id, brand.id)
        self.assertEqual(dto.name, brand.name)
        self.assertEqual(dto.description, brand.description)

    def test_category_model_dto_factory_build_many_returns_dtos(self) -> None:
        """ Verify CategoryModelDTOFactory.build_many returns DTOs for every model. """
        first = CategoryModel.objects.create(name="Industrial", slug="industrial")
        second = CategoryModel.objects.create(name="Lubricacion", slug="lubricacion")

        dtos = CategoryModelDTOFactory.build_many([first, second])

        self.assertEqual([dto.id for dto in dtos], [first.id, second.id])
        self.assertEqual([dto.slug for dto in dtos], [first.slug, second.slug])
