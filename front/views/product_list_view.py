""" Public single-tenant product list view for storefront browsing. """

from django.core.paginator import Paginator
from django.views.generic import TemplateView
from catalog.models import ProductModel
from front.views.public_site_view_mixin import PublicSiteViewMixin


class ProductListView(PublicSiteViewMixin, TemplateView):
    """ Render the public product catalog with pagination. """

    template_name = "pages/product_list.html"
    paginate_by = 12

    def get_product_queryset(self):
        """ Return the tenant-scoped active product queryset for the storefront.

        Returns:
            django.db.models.QuerySet[ProductModel]: Public active product queryset.
        """
        tenant = self.get_tenant()
        return (
            ProductModel.objects.for_tenant(tenant)
            .active()
            .with_related()
            .prefetch_related("images", "variants")
            .order_by("name")
        )

    def build_page_url(self, page_number: int) -> str:
        """ Build one catalog page URL.

        Args:
            page_number: Page number to encode into the URL.

        Returns:
            str: Catalog URL with query parameters when needed.
        """
        if page_number <= 1:
            return self.request.path
        return f"{self.request.path}?page={page_number}"

    def paginate_product_cards(self, product_queryset) -> tuple[list[dict[str, object]], object]:
        """ Paginate the product queryset and build card payloads.

        Args:
            product_queryset: Product queryset to paginate.

        Returns:
            tuple[list[dict[str, object]], object]: Current page card payloads and page object.
        """
        paginator = Paginator(product_queryset, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        product_cards = [self.build_product_card_data(product) for product in page_obj.object_list]
        return product_cards, page_obj

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """ Return the public catalog context.

        Args:
            **kwargs: Generic template-view keyword arguments.

        Returns:
            dict[str, object]: Public catalog context.
        """
        context = super().get_context_data(**kwargs)
        product_cards, page_obj = self.paginate_product_cards(self.get_product_queryset())

        context.update(
            product_cards=product_cards,
            page_obj=page_obj,
            is_paginated=page_obj.paginator.num_pages > 1,
            pagination_links=[
                {
                    "number": page_number,
                    "url": self.build_page_url(page_number),
                    "is_current": page_obj.number == page_number,
                }
                for page_number in page_obj.paginator.page_range
            ],
            pagination_prev_url=self.build_page_url(page_obj.previous_page_number()) if page_obj.has_previous() else "",
            pagination_next_url=self.build_page_url(page_obj.next_page_number()) if page_obj.has_next() else "",
        )
        return context
