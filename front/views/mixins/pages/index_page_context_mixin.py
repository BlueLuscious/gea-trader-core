""" Page-scoped context assembly for the public storefront home view. """

from catalog.models import ProductModel
from masterdata.models import CategoryModel
from tenancy.models import TenantModel


class IndexPageContextMixin:
    """ Build the page-specific context required by the public home view. """

    def get_featured_product_models(
        self,
        tenant: TenantModel,
        limit: int = 6,
    ) -> list[ProductModel]:
        """ Return featured active products for the public home page.

        Args:
            tenant: Active public tenant.
            limit: Maximum number of products to return.

        Returns:
            list[ProductModel]: Featured product models ordered for home usage.
        """
        return list(
            ProductModel.objects.for_tenant(tenant)
            .active()
            .featured()
            .with_related()
            .prefetch_related("images")
            .order_by("name")[:limit]
        )

    def get_root_categories_with_featured_fallback(
        self,
        tenant: TenantModel,
        limit: int,
    ) -> list[CategoryModel]:
        """ Return root categories preferring featured entries and filling with active fallbacks.

        Args:
            tenant: Active public tenant.
            limit: Maximum number of categories to return.

        Returns:
            list[CategoryModel]: Root categories ordered for home rendering.
        """
        featured_categories = list(
            CategoryModel.objects.for_tenant(tenant)
            .active()
            .roots()
            .featured()
            .order_by("sort_order", "name")[:limit]
        )
        if len(featured_categories) >= limit:
            return featured_categories

        fallback_queryset = (
            CategoryModel.objects.for_tenant(tenant)
            .active()
            .roots()
            .exclude(pk__in=[category.pk for category in featured_categories])
            .order_by("sort_order", "name")[: limit - len(featured_categories)]
        )
        return [*featured_categories, *list(fallback_queryset)]

    def get_recent_products(
        self,
        tenant: TenantModel,
        limit: int = 8,
    ) -> list[ProductModel]:
        """ Return the newest active products for the public home page.

        Args:
            tenant: Active public tenant.
            limit: Maximum number of products to return.

        Returns:
            list[ProductModel]: Newest active products ordered from newest to oldest.
        """
        return list(
            ProductModel.objects.for_tenant(tenant)
            .active()
            .with_related()
            .prefetch_related("images")
            .order_by("-created_at", "-id")[:limit]
        )

    def get_root_category_count(self, tenant: TenantModel) -> int:
        """ Return the amount of active root categories for the tenant.

        Args:
            tenant: Active public tenant.

        Returns:
            int: Active root-category count.
        """
        return CategoryModel.objects.for_tenant(tenant).active().roots().count()

    def get_active_subcategory_count(self, tenant: TenantModel) -> int:
        """ Return the amount of active non-root categories for the tenant.

        Args:
            tenant: Active public tenant.

        Returns:
            int: Active subcategory count.
        """
        return CategoryModel.objects.for_tenant(tenant).active().exclude(parent__isnull=True).count()

    def build_index_page_context(self) -> dict[str, object]:
        """ Build the page-specific context for the public storefront home page.

        Returns:
            dict[str, object]: Home-page context payload.
        """
        tenant = self.get_tenant()
        featured_products = self.get_featured_product_models(tenant, limit=6)
        featured_root_categories = self.get_root_categories_with_featured_fallback(tenant, limit=3)
        recent_products = self.get_recent_products(tenant)
        home_root_categories = self.get_root_categories_with_featured_fallback(tenant, limit=6)

        return {
            "featured_products": self.build_product_dtos(featured_products),
            "featured_root_categories": self.build_category_dtos(featured_root_categories),
            "featured_product_cards": [self.build_product_card_data(product) for product in featured_products],
            "recent_product_cards": [self.build_product_card_data(product) for product in recent_products],
            "featured_root_category_cards": [
                self.build_category_card_data(category) for category in featured_root_categories
            ],
            "home_root_category_cards": [
                self.build_category_card_data(category) for category in home_root_categories
            ],
            "home_root_category_count_text": str(self.get_root_category_count(tenant)),
            "home_subcategory_count_text": str(self.get_active_subcategory_count(tenant)),
        }

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """ Extend the template context with home-page-specific storefront data.

        Args:
            **kwargs: Generic template-view keyword arguments.

        Returns:
            dict[str, object]: Public home context.
        """
        context = super().get_context_data(**kwargs)
        context.update(self.build_index_page_context())
        return context
