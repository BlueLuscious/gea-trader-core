""" Public single-tenant product detail view for the front app. """

from catalog.models import ProductModel
from front.views.base import PublicPageDetailView
from front.views.mixins.pages import CatalogDataMixin, ProductDetailPageContextMixin


class ProductDetailView(ProductDetailPageContextMixin, CatalogDataMixin, PublicPageDetailView):
    """ Render one public product detail page with active variants. """

    model = ProductModel
    template_name = "pages/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"
