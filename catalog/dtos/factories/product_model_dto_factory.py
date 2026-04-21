""" Factory helpers for transforming catalog products into DTOs. """

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
        default_variant = instance.get_default_variant()
        return ProductModelDTO(
            id=instance.id,
            brand_id=instance.brand_id,
            category_id=instance.category_id,
            brand_name=instance.brand.name if instance.brand is not None else "",
            category_name=instance.category.name if instance.category is not None else "",
            name=instance.name,
            slug=instance.slug,
            short_description=instance.short_description,
            description=instance.description,
            sku_base=instance.sku_base,
            is_active=instance.is_active,
            is_featured=instance.is_featured,
            requires_quote=instance.requires_quote,
            active_variant_count=instance.get_active_variant_count(),
            has_multiple_active_variants=instance.has_multiple_active_variants(),
            default_variant_name=(
                default_variant.name or default_variant.sku
                if default_variant is not None
                else ""
            ),
            image_url=instance.get_preferred_image_url(),
            image_alt=instance.get_preferred_image_alt(),
            public_price=instance.get_public_price(),
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
