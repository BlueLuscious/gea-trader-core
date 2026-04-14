""" Owner-oriented product admin form. """

from django import forms
from django.utils.translation import gettext_lazy as _
from catalog.models import ProductModel


class ProductModelAdminForm(forms.ModelForm):
    """ Owner-oriented product form with friendlier labels and guidance. """

    class Meta:
        """ Configure the form for the owner product admin. """

        model = ProductModel
        fields = "__all__"
        help_texts = {
            "slug": _("Usually created from the product name. Adjust it only when you need a custom URL."),
            "short_description": _("Short summary for compact cards and product lists."),
            "description": _("Full product description with the details customers should read."),
            "sku_base": _("Internal base reference used to identify this product family and its variants."),
            "requires_quote": _("Enable this when customers should request a quote instead of buying directly."),
        }
        labels = {
            "name": _("Product name"),
            "slug": _("URL slug"),
            "brand": _("Brand"),
            "category": _("Category"),
            "short_description": _("Short description"),
            "description": _("Full description"),
            "sku_base": _("Base SKU"),
            "is_active": _("Visible to customers"),
            "is_featured": _("Featured product"),
            "requires_quote": _("Request through quote"),
        }
