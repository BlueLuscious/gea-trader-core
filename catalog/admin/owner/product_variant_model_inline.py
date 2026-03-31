""" Owner inline admin for product variants. """

from unfold.admin import TabularInline
from catalog.models import ProductVariantModel


class ProductVariantModelInline(TabularInline):
    """ Inline editor for product variants inside the owner product admin. """

    model = ProductVariantModel
    tab = True
    show_count = True
    extra = 0
    can_delete = False
    fields = ("name", "sku", "price", "is_default", "is_active", "sort_order")
    ordering = ("sort_order", "name", "id")
    verbose_name = "Variant"
    verbose_name_plural = "Variants"
