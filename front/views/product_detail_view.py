""" Public single-tenant product detail view for the front app. """

from django.views.generic import DetailView
from catalog.models import ProductModel
from front.views.mixins.pages import CatalogPresentationMixin, ProductDetailPageContextMixin, TenantAwareMixin


class ProductDetailView(ProductDetailPageContextMixin, CatalogPresentationMixin, TenantAwareMixin, DetailView):
    """ Render one public product detail page with active variants. """

    model = ProductModel
    template_name = "pages/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"
