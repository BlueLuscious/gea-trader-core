""" Owner inline admin for product variants. """

from django.utils.translation import gettext_lazy as _
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
    verbose_name = _("Variant")
    verbose_name_plural = _("Variants")
