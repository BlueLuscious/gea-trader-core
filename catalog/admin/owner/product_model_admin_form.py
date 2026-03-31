""" Owner-oriented product admin form. """

from django import forms
from catalog.models import ProductModel


class ProductModelAdminForm(forms.ModelForm):
    """ Owner-oriented product form with friendlier labels and guidance. """

    class Meta:
        """ Configure the form for the owner product admin. """

        model = ProductModel
        fields = "__all__"
        help_texts = {
            "slug": "Created automatically from the product name. Adjust it only if you need a custom URL.",
            "short_description": "Short summary shown in compact product views.",
            "description": "Full product description with the details your customer should read.",
            "sku_base": "Internal base reference used to help identify this product and its variants.",
            "requires_quote": "Keep this enabled when the product should be requested through a quote instead of a direct sale.",
        }
        labels = {
            "name": "Product name",
            "slug": "URL slug",
            "brand": "Brand",
            "category": "Category",
            "short_description": "Short description",
            "description": "Full description",
            "sku_base": "Base SKU",
            "is_active": "Visible to customers",
            "is_featured": "Highlight this product",
            "requires_quote": "Request through quote",
        }
