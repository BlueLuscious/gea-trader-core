""" Owner inline admin for product images. """

from unfold.admin import StackedInline
from catalog.admin.owner.product_image_model_inline_formset import ProductImageModelInlineFormSet
from catalog.models import ProductImageModel


class ProductImageModelInline(StackedInline):
    """ Inline editor for product images inside the owner product admin. """

    model = ProductImageModel
    formset = ProductImageModelInlineFormSet
    tab = True
    show_count = True
    extra = 0
    fieldsets = (
        (
            "Image details",
            {
                "fields": (
                    ("image", "variant"),
                    ("alt_text", "is_primary"),
                    "sort_order",
                ),
            },
        ),
    )
    ordering = ("sort_order", "id")
    verbose_name = "Image"
    verbose_name_plural = "Images"
