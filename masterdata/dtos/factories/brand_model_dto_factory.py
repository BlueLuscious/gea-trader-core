""" Factory helpers for transforming brands into DTOs. """

from collections.abc import Iterable
from masterdata.dtos.brand_model_dto import BrandModelDTO
from masterdata.models import BrandModel


class BrandModelDTOFactory:
    """ Factory for transforming brand models into DTOs. """

    @staticmethod
    def build(instance: BrandModel) -> BrandModelDTO:
        """ Build a DTO from a model instance.

        Args:
            instance: Brand model instance.

        Returns:
            BrandModelDTO: Serialized brand representation.
        """
        return BrandModelDTO(
            id=instance.id,
            tenant_id=str(instance.tenant_id),
            name=instance.name,
            slug=instance.slug,
            description=instance.description,
            is_active=instance.is_active,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

    @classmethod
    def build_many(cls, instances: Iterable[BrandModel]) -> list[BrandModelDTO]:
        """ Build DTOs from multiple brand instances.

        Args:
            instances: Iterable of brand models.

        Returns:
            list[BrandModelDTO]: DTO list.
        """
        return [cls.build(instance) for instance in instances]
