""" Public single-tenant root category listing view for the storefront. """

from django.views.generic import TemplateView
from front.views.mixins.pages import CatalogPresentationMixin, CategoryListPageContextMixin, TenantAwareMixin


class CategoryListView(CategoryListPageContextMixin, CatalogPresentationMixin, TenantAwareMixin, TemplateView):
    """ Render the public list of root categories with their active subcategories. """

    template_name = "pages/category_list.html"
