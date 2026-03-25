from collections.abc import Iterable
from masterdata.dtos.category_model_dto import CategoryModelDTO
from masterdata.models import CategoryModel


class CategoryModelDTOFactory:
    """ Factory for transforming category models into DTOs. """

    @staticmethod
    def build(instance: CategoryModel) -> CategoryModelDTO:
        """ Build a DTO from a model instance.

        Args:
            instance: Category model instance.

        Returns:
            CategoryModelDTO: Serialized category representation.
        """
        return CategoryModelDTO(
            id=instance.id,
            name=instance.name,
            slug=instance.slug,
            description=instance.description,
            parent_id=instance.parent_id,
            sort_order=instance.sort_order,
            is_active=instance.is_active,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

    @classmethod
    def build_many(cls, instances: Iterable[CategoryModel]) -> list[CategoryModelDTO]:
        """ Build DTOs from multiple category instances.

        Args:
            instances: Iterable of category models.

        Returns:
            list[CategoryModelDTO]: DTO list.
        """
        return [cls.build(instance) for instance in instances]
