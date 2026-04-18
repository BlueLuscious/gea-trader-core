""" Factory helpers for transforming catalog images into DTOs. """

from collections.abc import Iterable
from catalog.dtos.product_image_model_dto import ProductImageModelDTO
from catalog.models import ProductImageModel


class ProductImageModelDTOFactory:
    """ Factory for transforming product image models into DTOs. """

    @staticmethod
    def build(instance: ProductImageModel) -> ProductImageModelDTO:
        """ Build a product image DTO.

        Args:
            instance: Product image model instance.

        Returns:
            ProductImageModelDTO: Serialized image.
        """
        return ProductImageModelDTO(
            id=instance.id,
            product_id=instance.product_id,
            variant_id=instance.variant_id,
            image_name=instance.image.name if instance.image else "",
            alt_text=instance.alt_text,
            sort_order=instance.sort_order,
            is_primary=instance.is_primary,
            created_at=instance.created_at,
        )

    @classmethod
    def build_many(cls, instances: Iterable[ProductImageModel]) -> list[ProductImageModelDTO]:
        """ Build multiple image DTOs.

        Args:
            instances: Iterable of product image models.

        Returns:
            list[ProductImageModelDTO]: DTO list.
        """
        return [cls.build(instance) for instance in instances]
