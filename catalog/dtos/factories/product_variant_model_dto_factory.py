""" Factory helpers for transforming catalog variants into DTOs. """

from collections.abc import Iterable
from catalog.dtos.product_variant_model_dto import ProductVariantModelDTO
from catalog.models import ProductVariantModel


class ProductVariantModelDTOFactory:
    """ Factory for transforming product variant models into DTOs. """

    @staticmethod
    def build_display_name(instance: ProductVariantModel) -> str:
        """ Build one public variant label.

        Args:
            instance: Product variant model instance.

        Returns:
            str: Variant name or SKU fallback.
        """
        return instance.name or instance.sku

    @staticmethod
    def build_attributes_display(instance: ProductVariantModel) -> list[str]:
        """ Build human-readable attribute lines for one variant.

        Args:
            instance: Product variant model instance.

        Returns:
            list[str]: Formatted attribute lines.
        """
        attributes = instance.attributes_json if isinstance(instance.attributes_json, dict) else {}
        formatted_attributes: list[str] = []
        for key, value in attributes.items():
            key_label = str(key).replace("_", " ").strip().capitalize()
            value_label = str(value).strip()
            if not key_label or not value_label:
                continue
            formatted_attributes.append(f"{key_label}: {value_label}")
        return formatted_attributes

    @staticmethod
    def build_price_data(instance: ProductVariantModel, product_requires_quote: bool) -> tuple[str, str]:
        """ Build normalized price values for storefront rendering.

        Args:
            instance: Product variant model instance.
            product_requires_quote: Whether the parent product is quote-only.

        Returns:
            tuple[str, str]: Raw price value and public label text.
        """
        if product_requires_quote or instance.price is None:
            return "", "Cotización"

        return str(instance.price), f"ARS {instance.price:.2f}"

    @staticmethod
    def build(
        instance: ProductVariantModel,
        *,
        product_requires_quote: bool = False,
        image_url: str = "",
        image_alt: str = "",
    ) -> ProductVariantModelDTO:
        """ Build a variant DTO.

        Args:
            instance: Product variant model instance.
            product_requires_quote: Whether the parent product is quote-only.
            image_url: Preferred image URL for the variant.
            image_alt: Preferred image alt text for the variant.

        Returns:
            ProductVariantModelDTO: Serialized variant.
        """
        price_value, price_text = ProductVariantModelDTOFactory.build_price_data(instance, product_requires_quote)
        display_name = ProductVariantModelDTOFactory.build_display_name(instance)
        return ProductVariantModelDTO(
            id=instance.id,
            product_id=instance.product_id,
            name=instance.name,
            display_name=display_name,
            sku=instance.sku,
            attributes_json=dict(instance.attributes_json or {}),
            attributes_display=ProductVariantModelDTOFactory.build_attributes_display(instance),
            price=instance.price,
            price_value=price_value,
            price_text=price_text,
            is_default=instance.is_default,
            is_active=instance.is_active,
            sort_order=instance.sort_order,
            image_url=image_url,
            image_alt=image_alt or display_name,
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
