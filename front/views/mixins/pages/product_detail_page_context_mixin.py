""" Page-scoped context assembly for the public storefront product detail. """

from django.db.models import QuerySet
from catalog.dtos import ProductVariantModelDTO
from catalog.dtos.factories import ProductModelDTOFactory, ProductVariantModelDTOFactory
from catalog.models import ProductModel


class ProductDetailPageContextMixin:
    """ Build the page-specific context required by the public product detail view. """

    def get_queryset(self) -> QuerySet[ProductModel]:
        """ Return the public product queryset scoped to the active tenant.

        Returns:
            QuerySet[ProductModel]: Tenant-scoped active products.
        """
        tenant = self.get_tenant()
        return (
            ProductModel.objects.for_tenant(tenant)
            .active()
            .with_related()
            .prefetch_related("images", "variants")
        )

    def build_variant_dtos(self, product: ProductModel) -> list[ProductVariantModelDTO]:
        """ Build variant DTOs for the selected product.

        Args:
            product: Product detail object.

        Returns:
            list[ProductVariantModelDTO]: Variant DTO list sorted for rendering.
        """
        active_variants = list(product.variants.active().order_by("-is_default", "sort_order", "name", "id"))
        return [
            ProductVariantModelDTOFactory.build(
                variant,
                product_requires_quote=product.requires_quote,
                image_url=product.get_variant_image_url(variant),
                image_alt=product.get_variant_image_alt(variant),
            )
            for variant in active_variants
        ]

    def build_product_detail_page_context(self) -> dict[str, object]:
        """ Build the page-specific context for the public product detail page.

        Returns:
            dict[str, object]: Product-detail page context.
        """
        product = self.object
        return {
            "product_dto": ProductModelDTOFactory.build(product),
            "product_variants": self.build_variant_dtos(product),
        }

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """ Extend the template context with product-detail-specific storefront data.

        Args:
            **kwargs: Generic detail-view keyword arguments.

        Returns:
            dict[str, object]: Public product-detail context.
        """
        context = super().get_context_data(**kwargs)
        context.update(self.build_product_detail_page_context())
        return context
