""" Public single-tenant product list view for storefront browsing. """

from django.views.generic import TemplateView
from front.views.mixins.pages import CatalogPresentationMixin, ProductListPageContextMixin, TenantAwareMixin


class ProductListView(ProductListPageContextMixin, CatalogPresentationMixin, TenantAwareMixin, TemplateView):
    """ Render the public product catalog with pagination. """

    template_name = "pages/product_list.html"
