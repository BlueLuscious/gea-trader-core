""" Public single-tenant category page for storefront product browsing. """

from django.core.paginator import Paginator
from django.http import Http404
from django.views.generic import DetailView
from catalog.models import ProductModel
from front.views.public_site_view_mixin import PublicSiteViewMixin
from masterdata.dtos.factories import CategoryModelDTOFactory
from masterdata.models import CategoryModel


class CategoryProductListView(PublicSiteViewMixin, DetailView):
    """ Render one public category page with optional subcategory filtering. """

    model = CategoryModel
    template_name = "pages/category_product_list.html"
    context_object_name = "category"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    paginate_by = 12

    def get_queryset(self):
        """ Return active tenant-scoped categories for public browsing.

        Returns:
            django.db.models.QuerySet[CategoryModel]: Tenant-scoped active categories.
        """
        tenant = self.get_tenant()
        return CategoryModel.objects.for_tenant(tenant).active().select_related("parent")

    def get_subcategory_filter(self, category: CategoryModel) -> CategoryModel | None:
        """ Resolve the optional subcategory filter for the current category page.

        Args:
            category: Current category object resolved from the URL.

        Returns:
            CategoryModel | None: Selected subcategory or ``None`` when not filtering.

        Raises:
            Http404: When the requested subcategory does not belong to the current category.
        """
        subcategory_slug = (self.request.GET.get("subcategoria") or "").strip()
        if not subcategory_slug:
            return None

        subcategory = category.children.active().filter(slug=subcategory_slug).first()
        if subcategory is None:
            raise Http404("The requested subcategory does not belong to this category.")

        return subcategory

    def get_product_queryset(
        self,
        category: CategoryModel,
        selected_subcategory: CategoryModel | None,
    ):
        """ Build the product queryset for the current category context.

        Args:
            category: Current category page object.
            selected_subcategory: Optional direct child category used as a filter.

        Returns:
            django.db.models.QuerySet[ProductModel]: Product queryset ready for DTO/card building.
        """
        tenant = self.get_tenant()
        queryset = (
            ProductModel.objects.for_tenant(tenant)
            .active()
            .with_related()
            .prefetch_related("images", "variants")
            .order_by("name")
        )

        if selected_subcategory is not None:
            return queryset.filter(category=selected_subcategory)

        child_category_ids = list(category.children.active().values_list("id", flat=True))
        category_ids = [category.id, *child_category_ids]
        return queryset.filter(category_id__in=category_ids)

    def build_subcategory_links(
        self,
        category: CategoryModel,
        selected_subcategory: CategoryModel | None,
    ) -> list[dict[str, object]]:
        """ Build presentation data for category-level subfilters.

        Args:
            category: Current category page object.
            selected_subcategory: Optional direct child category used as a filter.

        Returns:
            list[dict[str, object]]: Link payloads for the template.
        """
        links: list[dict[str, object]] = [
            {
                "label": "Todas",
                "url": self.request.path,
                "is_active": selected_subcategory is None,
            }
        ]

        for subcategory in category.children.active().order_by("sort_order", "name"):
            links.append(
                {
                    "label": subcategory.name,
                    "url": self.build_page_url(1, subcategory_slug=subcategory.slug),
                    "is_active": selected_subcategory is not None and selected_subcategory.id == subcategory.id,
                }
            )

        return links

    def build_page_url(self, page_number: int, subcategory_slug: str = "") -> str:
        """ Build one category-page URL preserving supported query params.

        Args:
            page_number: Page number to encode into the URL.
            subcategory_slug: Optional selected subcategory slug.

        Returns:
            str: Category page URL with query parameters when needed.
        """
        query_parts: list[str] = []
        if subcategory_slug:
            query_parts.append(f"subcategoria={subcategory_slug}")
        if page_number > 1:
            query_parts.append(f"page={page_number}")

        if not query_parts:
            return self.request.path

        return f"{self.request.path}?{'&'.join(query_parts)}"

    def paginate_product_cards(
        self,
        product_queryset,
        selected_subcategory: CategoryModel | None,
    ) -> tuple[list[dict[str, object]], object]:
        """ Paginate the current category product queryset.

        Args:
            product_queryset: Product queryset already filtered for category context.
            selected_subcategory: Optional selected subcategory filter.

        Returns:
            tuple[list[dict[str, object]], object]: Current page card payloads and page object.
        """
        paginator = Paginator(product_queryset, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        product_cards = [self.build_product_card_data(product) for product in page_obj.object_list]

        for page_number in paginator.page_range:
            setattr(
                page_obj.paginator,
                f"page_url_{page_number}",
                self.build_page_url(
                    page_number,
                    subcategory_slug=selected_subcategory.slug if selected_subcategory is not None else "",
                ),
            )

        return product_cards, page_obj

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """ Return category page context for the public storefront.

        Args:
            **kwargs: Generic detail-view keyword arguments.

        Returns:
            dict[str, object]: Category page context.
        """
        context = super().get_context_data(**kwargs)
        category = self.object
        selected_subcategory = self.get_subcategory_filter(category)
        category_dto = CategoryModelDTOFactory.build(category)
        product_queryset = self.get_product_queryset(category, selected_subcategory)
        category_product_cards, page_obj = self.paginate_product_cards(product_queryset, selected_subcategory)

        context.update(
            category_dto=category_dto,
            category_banner_url=category.banner.url if category.banner else "",
            selected_subcategory=selected_subcategory,
            selected_subcategory_dto=(
                CategoryModelDTOFactory.build(selected_subcategory)
                if selected_subcategory is not None
                else None
            ),
            subcategory_links=self.build_subcategory_links(category, selected_subcategory),
            category_product_cards=category_product_cards,
            page_obj=page_obj,
            is_paginated=page_obj.paginator.num_pages > 1,
            pagination_links=[
                {
                    "number": page_number,
                    "url": self.build_page_url(
                        page_number,
                        subcategory_slug=selected_subcategory.slug if selected_subcategory is not None else "",
                    ),
                    "is_current": page_obj.number == page_number,
                }
                for page_number in page_obj.paginator.page_range
            ],
            pagination_prev_url=(
                self.build_page_url(
                    page_obj.previous_page_number(),
                    subcategory_slug=selected_subcategory.slug if selected_subcategory is not None else "",
                )
                if page_obj.has_previous()
                else ""
            ),
            pagination_next_url=(
                self.build_page_url(
                    page_obj.next_page_number(),
                    subcategory_slug=selected_subcategory.slug if selected_subcategory is not None else "",
                )
                if page_obj.has_next()
                else ""
            ),
        )
        return context
