""" Public single-tenant category page for storefront product browsing. """

from front.views.base import PublicPageDetailView
from front.views.mixins.pages import CatalogDataMixin, CategoryProductListPageContextMixin
from masterdata.models import CategoryModel


class CategoryProductListView(CategoryProductListPageContextMixin, CatalogDataMixin, PublicPageDetailView):
    """ Render one public category page with optional subcategory filtering. """

    model = CategoryModel
    template_name = "pages/category_product_list.html"
    context_object_name = "category"
    slug_field = "slug"
    slug_url_kwarg = "slug"
