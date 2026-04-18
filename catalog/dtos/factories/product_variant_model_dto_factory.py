""" Factory helpers for transforming catalog variants into DTOs. """

from collections.abc import Iterable
from catalog.dtos.product_variant_model_dto import ProductVariantModelDTO
from catalog.models import ProductVariantModel


class ProductVariantModelDTOFactory:
    """ Factory for transforming product variant models into DTOs. """

    @staticmethod
    def build(instance: ProductVariantModel) -> ProductVariantModelDTO:
        """ Build a variant DTO.

        Args:
            instance: Product variant model instance.

        Returns:
            ProductVariantModelDTO: Serialized variant.
        """
        return ProductVariantModelDTO(
            id=instance.id,
            product_id=instance.product_id,
            name=instance.name,
            sku=instance.sku,
            attributes_json=dict(instance.attributes_json or {}),
            price=instance.price,
            is_default=instance.is_default,
            is_active=instance.is_active,
            sort_order=instance.sort_order,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

    @classmethod
    def build_many(cls, instances: Iterable[ProductVariantModel]) -> list[ProductVariantModelDTO]:
        """ Build multiple variant DTOs.

        Args:
            instances: Iterable of product variant models.

        Returns:
            list[ProductVariantModelDTO]: DTO list.
        """
        return [cls.build(instance) for instance in instances]
