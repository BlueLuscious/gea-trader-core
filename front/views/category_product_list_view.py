""" Public single-tenant category page for storefront product browsing. """

from django.views.generic import DetailView
from front.views.mixins.pages import CatalogPresentationMixin, CategoryProductListPageContextMixin, TenantAwareMixin
from masterdata.models import CategoryModel


class CategoryProductListView(
    CategoryProductListPageContextMixin,
    CatalogPresentationMixin,
    TenantAwareMixin,
    DetailView,
):
    """ Render one public category page with optional subcategory filtering. """

    model = CategoryModel
    template_name = "pages/category_product_list.html"
    context_object_name = "category"
    slug_field = "slug"
    slug_url_kwarg = "slug"
