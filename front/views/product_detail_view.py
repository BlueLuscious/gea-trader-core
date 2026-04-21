""" Public single-tenant product detail view for the front app. """

from django.views.generic import DetailView
from catalog.dtos import ProductVariantModelDTO
from catalog.dtos.factories import ProductModelDTOFactory, ProductVariantModelDTOFactory
from catalog.models import ProductModel
from front.views.public_site_view_mixin import PublicSiteViewMixin


class ProductDetailView(PublicSiteViewMixin, DetailView):
    """ Render one public product detail page with active variants. """

    model = ProductModel
    template_name = "pages/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """ Return the public product queryset scoped to the active tenant.

        Returns:
            django.db.models.QuerySet[ProductModel]: Tenant-scoped active products.
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

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """ Return product detail context for the public page.

        Args:
            **kwargs: Generic template-view keyword arguments.

        Returns:
            dict[str, object]: Product detail context.
        """
        context = super().get_context_data(**kwargs)
        product = self.object
        context.update(
            product_dto=ProductModelDTOFactory.build(product),
            product_variants=self.build_variant_dtos(product),
        )
        return context
