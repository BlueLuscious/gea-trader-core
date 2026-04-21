""" Shared single-tenant public view helpers for the front app. """

from typing import Any
from django.http import Http404
from django.urls import reverse
from django.views.generic.base import ContextMixin
from catalog.dtos.factories import ProductModelDTOFactory
from catalog.models import ProductModel
from masterdata.dtos.factories import CategoryModelDTOFactory
from masterdata.models import CategoryModel
from tenancy.models import TenantBrandingModel, TenantModel


class PublicSiteViewMixin(ContextMixin):
    """ Resolve the single public tenant and provide shared storefront context. """

    tenant_context_name = "current_tenant"

    def get_tenant(self) -> TenantModel:
        """ Return the single active tenant that owns the public site.

        Returns:
            TenantModel: Active tenant used by the public site.

        Raises:
            Http404: When no active tenant is available for the public site.
        """
        tenant = TenantModel.objects.filter(is_active=True).order_by("created_at", "name").first()
        if tenant is None:
            raise Http404("No public tenant is available.")

        return tenant

    def get_brand_name(self, tenant: TenantModel) -> str:
        """ Return the public display name for the site tenant.

        Args:
            tenant: Active public tenant.

        Returns:
            str: Branding display name or fallback tenant name.
        """
        branding: TenantBrandingModel = getattr(tenant, "branding", None)
        if branding is not None and branding.display_name:
            return branding.display_name

        return tenant.name

    def build_layout_context(self, tenant: TenantModel) -> dict[str, object]:
        """ Build the shared navigation context for public pages.

        Args:
            tenant: Active public tenant.

        Returns:
            dict[str, object]: Shared layout context for the base template.
        """
        branding: TenantBrandingModel = getattr(tenant, "branding", None)
        logo_light_url = (
            branding.logo_light.url
            if branding is not None and getattr(branding, "logo_light", None)
            else None
        )
        logo_dark_url = (
            branding.logo_dark.url
            if branding is not None and getattr(branding, "logo_dark", None)
            else logo_light_url
        )
        return {
            self.tenant_context_name: tenant,
            "site_brand_name": self.get_brand_name(tenant),
            "site_logo_light_url": logo_light_url,
            "site_logo_dark_url": logo_dark_url,
            "site_home_url": "/",
            "site_products_url": reverse("product_list"),
            "site_categories_url": reverse("category_list"),
            "carrousel_prev_attrs": {"carousel-prev": "true"},
            "carrousel_next_attrs": {"carousel-next": "true"},
        }

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """ Extend context with the resolved public tenant and shared navigation.

        Args:
            **kwargs: Generic view context keyword arguments.

        Returns:
            dict[str, object]: Context extended with public-site layout data.
        """
        context = super().get_context_data(**kwargs)
        tenant = self.get_tenant()
        context.update(self.build_layout_context(tenant))
        return context

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

    def get_featured_products(self, tenant: TenantModel, limit: int = 6) -> list[object]:
        """ Return featured active product DTOs for the public tenant.

        Args:
            tenant: Active public tenant.
            limit: Maximum number of products to return.

        Returns:
            list[object]: Featured product DTO list.
        """
        queryset = (
            ProductModel.objects.for_tenant(tenant)
            .active()
            .featured()
            .with_related()
            .prefetch_related("images")
            .order_by("name")[:limit]
        )
        return self.build_product_dtos(queryset)

    def get_featured_root_categories(self, tenant: TenantModel, limit: int = 3) -> list[object]:
        """ Return curated root-category DTOs for the public home page.

        Args:
            tenant: Active public tenant.
            limit: Maximum number of categories to return.

        Returns:
            list[object]: Featured root-category DTO list.
        """
        featured_queryset = (
            CategoryModel.objects.for_tenant(tenant)
            .active()
            .roots()
            .featured()
            .order_by("sort_order", "name")[:limit]
        )
        featured_categories = list(featured_queryset)
        if len(featured_categories) < limit:
            fallback_queryset = (
                CategoryModel.objects.for_tenant(tenant)
                .active()
                .roots()
                .exclude(pk__in=[category.pk for category in featured_categories])
                .order_by("sort_order", "name")[: limit - len(featured_categories)]
            )
            featured_categories.extend(list(fallback_queryset))

        return self.build_category_dtos(featured_categories)

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
