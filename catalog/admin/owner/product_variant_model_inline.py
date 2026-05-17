""" Owner inline admin for product variants. """

from django.utils.translation import gettext_lazy as _
from unfold.admin import StackedInline
from catalog.admin.owner.product_variant_model_inline_form import ProductVariantModelInlineForm
from catalog.admin.owner.product_variant_model_inline_formset import ProductVariantModelInlineFormSet
from catalog.models import ProductVariantModel


class ProductVariantModelInline(StackedInline):
    """ Inline editor for product variants inside the owner product admin. """

    model = ProductVariantModel
    form = ProductVariantModelInlineForm
    formset = ProductVariantModelInlineFormSet
    tab = True
    show_count = True
    extra = 0
    can_delete = False
    fields = ("name", "sku", "attributes_json", "price", "is_default", "is_active", "sort_order")
    ordering = ("sort_order", "name", "id")
    verbose_name = _("Variant")
    verbose_name_plural = _("Variants")
