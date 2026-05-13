""" Public single-tenant root category listing view for the storefront. """

from front.views.base import PublicPageTemplateView
from front.views.mixins.pages import CatalogDataMixin, CategoryListPageContextMixin


class CategoryListView(CategoryListPageContextMixin, CatalogDataMixin, PublicPageTemplateView):
    """ Render the public list of root categories with their active subcategories. """

    template_name = "pages/category_list.html"
