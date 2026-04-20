""" Public single-tenant home view for the front app. """

from django.views.generic import TemplateView
from catalog.models import ProductModel
from masterdata.models import CategoryModel
from front.views.public_site_view_mixin import PublicSiteViewMixin


class IndexView(PublicSiteViewMixin, TemplateView):
    """ Render the public single-tenant storefront home page. """

    template_name = "pages/index.html"

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
            featured_root_category_cards=[
                self.build_category_card_data(category) for category in featured_root_categories
            ],
        )
        return context
