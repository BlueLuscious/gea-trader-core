""" Presentation helpers for storefront product and category payloads. """

from typing import Any
from django.urls import reverse
from catalog.dtos.factories import ProductModelDTOFactory
from catalog.models import ProductModel
from masterdata.dtos.factories import CategoryModelDTOFactory
from masterdata.models import CategoryModel


class CatalogDataMixin:
    """ Build reusable storefront DTO and card payloads. """

    def build_product_dtos(self, queryset: Any) -> list[object]:
        """ Build product DTOs from one queryset or iterable.

        Args:
            queryset: Product queryset or iterable.

        Returns:
            list[object]: Product DTO list.
        """
        return ProductModelDTOFactory.build_many(list(queryset))

    def build_category_dtos(self, queryset: Any) -> list[object]:
        """ Build category DTOs from one queryset or iterable.

        Args:
            queryset: Category queryset or iterable.

        Returns:
            list[object]: Category DTO list.
        """
        return CategoryModelDTOFactory.build_many(list(queryset))

    def build_product_card_data(self, product: ProductModel) -> dict[str, object]:
        """ Build one product card payload for public storefront templates.

        Args:
            product: Product model instance.

        Returns:
            dict[str, object]: Product presentation payload.
        """
        product_dto = ProductModelDTOFactory.build(product)
        return {
            "product_id": str(product.id),
            "dto": product_dto,
            "name": product_dto.name,
            "slug": product_dto.slug,
            "short_description": product_dto.short_description,
            "description": product_dto.description,
            "image_url": product_dto.image_url,
            "image_alt": product_dto.image_alt,
            "brand_name": product_dto.brand_name,
            "category_name": product_dto.category_name,
            "url": reverse("product_detail", kwargs={"slug": product_dto.slug}),
            "requires_quote": product_dto.requires_quote,
            "public_price": product_dto.public_price,
            "price_value": str(product_dto.public_price) if product_dto.public_price is not None else "",
            "price_text": (
                f"ARS {product_dto.public_price:.2f}"
                if product_dto.public_price is not None
                else "Cotización"
            ),
            "variant_count": product_dto.active_variant_count,
            "variant_badge_text": (
                f"{product_dto.active_variant_count} variantes"
                if product_dto.has_multiple_active_variants
                else ""
            ),
        }

    def build_category_card_data(self, category: CategoryModel) -> dict[str, object]:
        """ Build one category card payload for public storefront templates.

        Args:
            category: Category model instance.

        Returns:
            dict[str, object]: Category presentation payload.
        """
        category_dto = CategoryModelDTOFactory.build(category)
        return {
            "dto": category_dto,
            "name": category_dto.name,
            "slug": category_dto.slug,
            "description": category_dto.description,
            "banner_url": category.banner.url if category.banner else "",
            "url": reverse("category_product_list", kwargs={"slug": category_dto.slug}),
            "is_featured": category_dto.is_featured,
        }
