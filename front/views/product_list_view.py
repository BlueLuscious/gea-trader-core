""" Public single-tenant product list view for storefront browsing. """

from front.views.base import PublicPageTemplateView
from front.views.mixins.pages import CatalogDataMixin, ProductListPageContextMixin


class ProductListView(ProductListPageContextMixin, CatalogDataMixin, PublicPageTemplateView):
    """ Render the public product catalog with pagination. """

    template_name = "pages/product_list.html"
