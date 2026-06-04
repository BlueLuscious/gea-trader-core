""" Owner inline form for product variants. """

from django import forms
from django.utils.translation import gettext_lazy as _
from catalog.models import ProductVariantModel
from core.forms import JsonKeyValueField


class ProductVariantModelInlineForm(forms.ModelForm):
    """ Keep one focused and reusable owner form contract for product variants. """

    attributes_json = JsonKeyValueField(
        label=_("Variant attributes"),
        help_text=_("Add public variant details as key-value pairs, such as size or packaging."),
        key_label=_("Attribute key"),
        value_label=_("Attribute value"),
        add_label=_("Add attribute"),
        remove_label=_("Remove attribute"),
        required=False,
    )

    def __init__(self, *args: object, requires_quote: bool | None = None, **kwargs: object) -> None:
        """ Build one owner inline variant form with pricing guidance for the current product flow.

        Args:
            *args: Positional form arguments.
            requires_quote: Current product quote behavior when available.
            **kwargs: Keyword form arguments.
        """
        super().__init__(*args, **kwargs)

        if requires_quote is True:
            self.fields["price"].help_text = _(
                "Optional internal price. Customers still request a quote for this product."
            )
        elif requires_quote is False:
            self.fields["price"].help_text = _(
                "Required on the default variant when the product is directly purchasable."
            )

        self.fields["sku"].required = False

    class Meta:
        """ Configure the owner inline variant form. """

        model = ProductVariantModel
        fields = ("name", "sku", "attributes_json", "price", "is_default", "is_active", "sort_order")
        labels = {
            "name": _("Variant name"),
            "sku": _("Variant SKU"),
            "attributes_json": _("Variant attributes"),
            "price": _("Price"),
            "is_default": _("Default variant"),
            "is_active": _("Available for selection"),
            "sort_order": _("Display order"),
        }
        help_texts = {
            "name": _("Optional customer-facing name for this specific variant."),
            "sku": _("Optional unique internal reference. Leave it empty to use the product base SKU."),
            "attributes_json": _("Add public variant details as key-value pairs, such as size or packaging."),
            "price": _("Optional direct price for this variant when it does not rely only on quotes."),
            "is_default": _("Choose exactly one default variant for each product."),
            "is_active": _("Turn this off to keep the variant without offering it."),
            "sort_order": _("Lower values appear first in admin and customer-facing variant lists."),
        }
