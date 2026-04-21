""" Public single-tenant home view for the front app. """

from django.views.generic import TemplateView
from catalog.models import ProductModel
from masterdata.models import CategoryModel
from front.views.public_site_view_mixin import PublicSiteViewMixin


class IndexView(PublicSiteViewMixin, TemplateView):
    """ Render the public single-tenant storefront home page. """

    template_name = "pages/index.html"

    def get_recent_products(self, tenant: object, limit: int = 8) -> list[ProductModel]:
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

    def get_home_root_categories(self, tenant: object, limit: int = 6) -> list[CategoryModel]:
        """ Return curated root categories for the home categories section.

        Args:
            tenant: Active public tenant.
            limit: Maximum number of root categories to return.

        Returns:
            list[CategoryModel]: Root categories ordered for home display.
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

        fallback_categories = list(
            CategoryModel.objects.for_tenant(tenant)
            .active()
            .roots()
            .exclude(pk__in=[category.pk for category in featured_categories])
            .order_by("sort_order", "name")[: limit - len(featured_categories)]
        )
        return [*featured_categories, *fallback_categories]

    def get_root_category_count(self, tenant: object) -> int:
        """ Return the amount of active root categories for the tenant.

        Args:
            tenant: Active public tenant.

        Returns:
            int: Active root-category count.
        """
        return CategoryModel.objects.for_tenant(tenant).active().roots().count()

    def get_active_subcategory_count(self, tenant: object) -> int:
        """ Return the amount of active non-root categories for the tenant.

        Args:
            tenant: Active public tenant.

        Returns:
            int: Active subcategory count.
        """
        return CategoryModel.objects.for_tenant(tenant).active().exclude(parent__isnull=True).count()

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """ Return the public home context.

        Args:
            **kwargs: Generic template-view keyword arguments.

        Returns:
            dict[str, object]: Public home context.
        """
        context = super().get_context_data(**kwargs)
        tenant = self.get_tenant()
        featured_products_queryset = (
            ProductModel.objects.for_tenant(tenant)
            .active()
            .featured()
            .with_related()
            .prefetch_related("images")
            .order_by("name")[:6]
        )
        featured_root_categories_queryset = (
            CategoryModel.objects.for_tenant(tenant)
            .active()
            .roots()
            .featured()
            .order_by("sort_order", "name")[:3]
        )
        featured_root_categories = list(featured_root_categories_queryset)
        recent_products = self.get_recent_products(tenant)
        home_root_categories = self.get_home_root_categories(tenant)
        if len(featured_root_categories) < 3:
            fallback_root_categories_queryset = (
                CategoryModel.objects.for_tenant(tenant)
                .active()
                .roots()
                .exclude(pk__in=[category.pk for category in featured_root_categories])
                .order_by("sort_order", "name")[: 3 - len(featured_root_categories)]
            )
            featured_root_categories.extend(list(fallback_root_categories_queryset))

        context.update(
            featured_products=self.get_featured_products(tenant),
            featured_root_categories=self.get_featured_root_categories(tenant),
            featured_product_cards=[self.build_product_card_data(product) for product in featured_products_queryset],
            recent_product_cards=[self.build_product_card_data(product) for product in recent_products],
            featured_root_category_cards=[
                self.build_category_card_data(category) for category in featured_root_categories
            ],
            home_root_category_cards=[
                self.build_category_card_data(category) for category in home_root_categories
            ],
            home_root_category_count_text=str(self.get_root_category_count(tenant)),
            home_subcategory_count_text=str(self.get_active_subcategory_count(tenant)),
        )
        return context
