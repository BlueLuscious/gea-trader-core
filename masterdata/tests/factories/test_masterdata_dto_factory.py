from core.testing.base import LoggedTestCase
from masterdata.dtos.factories import BrandModelDTOFactory, CategoryModelDTOFactory
from masterdata.models import BrandModel, CategoryModel
from tenancy.models import TenantModel


class TestMasterdataDTOFactory(LoggedTestCase):
    """ Cover masterdata DTO factories. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for DTO factory ownership tests.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_brand_model_dto_factory_build_maps_fields(self) -> None:
        """ Verify BrandModelDTOFactory.build maps brand fields into a DTO. """
        tenant = self._create_tenant("brand-dto-factory")
        brand = BrandModel.objects.create(tenant=tenant, name="GEA", slug="gea", description="Industrial")

        dto = BrandModelDTOFactory.build(brand)

        self.assertEqual(dto.id, brand.id)
        self.assertEqual(dto.tenant_id, str(tenant.pk))
        self.assertEqual(dto.name, brand.name)
        self.assertEqual(dto.description, brand.description)

    def test_category_model_dto_factory_build_many_returns_dtos(self) -> None:
        """ Verify CategoryModelDTOFactory.build_many returns DTOs for every model. """
        tenant = self._create_tenant("category-dto-factory")
        first = CategoryModel.objects.create(tenant=tenant, name="Industrial", slug="industrial")
        second = CategoryModel.objects.create(tenant=tenant, name="Lubricacion", slug="lubricacion")

        dtos = CategoryModelDTOFactory.build_many([first, second])

        self.assertEqual([dto.id for dto in dtos], [first.id, second.id])
        self.assertEqual([dto.tenant_id for dto in dtos], [str(tenant.pk), str(tenant.pk)])
        self.assertEqual([dto.slug for dto in dtos], [first.slug, second.slug])
