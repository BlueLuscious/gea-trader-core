from collections.abc import Iterable
from catalog.dtos.product_model_dto import ProductModelDTO
from catalog.models import ProductModel


class ProductModelDTOFactory:
    """ Factory for transforming product models into DTOs. """

    @staticmethod
    def build(instance: ProductModel) -> ProductModelDTO:
        """ Build a product DTO.

        Args:
            instance: Product model instance.

        Returns:
            ProductModelDTO: Serialized product.
        """
        return ProductModelDTO(
            id=instance.id,
            brand_id=instance.brand_id,
            category_id=instance.category_id,
            name=instance.name,
            slug=instance.slug,
            short_description=instance.short_description,
            description=instance.description,
            sku_base=instance.sku_base,
            is_active=instance.is_active,
            is_featured=instance.is_featured,
            requires_quote=instance.requires_quote,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

    @classmethod
    def build_many(cls, instances: Iterable[ProductModel]) -> list[ProductModelDTO]:
        """ Build multiple product DTOs.

        Args:
            instances: Iterable of product models.

        Returns:
            list[ProductModelDTO]: DTO list.
        """
        return [cls.build(instance) for instance in instances]
