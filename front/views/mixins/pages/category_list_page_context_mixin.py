""" Page-scoped context assembly for the public storefront category list. """

from django.core.paginator import Paginator
from masterdata.models import CategoryModel


class CategoryListPageContextMixin:
    """ Build the page-specific context required by the public category list view. """

    paginate_by = 12

    def get_root_categories(self) -> list[CategoryModel]:
        """ Return active root categories for the current public tenant.

        Returns:
            list[CategoryModel]: Active root categories with prefetched active children.
        """
        tenant = self.get_tenant()
        return list(
            CategoryModel.objects.for_tenant(tenant)
            .active()
            .roots()
            .prefetch_related("children")
            .order_by("sort_order", "name")
        )

    def build_category_groups(self, categories: list[CategoryModel]) -> list[dict[str, object]]:
        """ Build root-category groups for the category index template.

        Args:
            categories: Root categories to expose on the page.

        Returns:
            list[dict[str, object]]: Presentation payload for root categories and children.
        """
        category_groups: list[dict[str, object]] = []
        for category in categories:
            children = [
                self.build_category_card_data(child)
                for child in category.children.all()
                if child.is_active
            ]
            children.sort(key=lambda child: (child["dto"].sort_order, child["name"]))
            category_groups.append(
                {
                    "root": self.build_category_card_data(category),
                    "children": children,
                    "children_count": len(children),
                    "children_count_text": str(len(children)),
                }
            )
        return category_groups

    def build_page_url(self, page_number: int) -> str:
        """ Build one root-category index URL.

        Args:
            page_number: Page number to encode into the URL.

        Returns:
            str: Category index URL with query parameters when needed.
        """
        if page_number <= 1:
            return self.request.path
        return f"{self.request.path}?page={page_number}"

    def paginate_category_groups(
        self,
        category_groups: list[dict[str, object]],
    ) -> tuple[list[dict[str, object]], object]:
        """ Paginate root-category groups for the public category index.

        Args:
            category_groups: Root-category groups already prepared for rendering.

        Returns:
            tuple[list[dict[str, object]], object]: Current page groups and page object.
        """
        paginator = Paginator(category_groups, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        return list(page_obj.object_list), page_obj

    def build_category_list_page_context(self) -> dict[str, object]:
        """ Build the page-specific context for the public root-category listing page.

        Returns:
            dict[str, object]: Category-list page context.
        """
        root_categories = self.get_root_categories()
        category_groups = self.build_category_groups(root_categories)
        paginated_category_groups, page_obj = self.paginate_category_groups(category_groups)
        root_category_count = len(root_categories)
        child_category_count = sum(group["children_count"] for group in category_groups)
        return {
            "category_groups": paginated_category_groups,
            "root_category_cards": [self.build_category_card_data(category) for category in root_categories],
            "root_category_count": root_category_count,
            "root_category_count_text": str(root_category_count),
            "child_category_count": child_category_count,
            "child_category_count_text": str(child_category_count),
            "page_obj": page_obj,
            "is_paginated": page_obj.paginator.num_pages > 1,
            "pagination_links": [
                {
                    "number": page_number,
                    "url": self.build_page_url(page_number),
                    "is_current": page_obj.number == page_number,
                }
                for page_number in page_obj.paginator.page_range
            ],
            "pagination_prev_url": self.build_page_url(page_obj.previous_page_number()) if page_obj.has_previous() else "",
            "pagination_next_url": self.build_page_url(page_obj.next_page_number()) if page_obj.has_next() else "",
        }

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """ Extend the template context with category-list-specific storefront data.

        Args:
            **kwargs: Generic template-view keyword arguments.

        Returns:
            dict[str, object]: Public category-list context.
        """
        context = super().get_context_data(**kwargs)
        context.update(self.build_category_list_page_context())
        return context
