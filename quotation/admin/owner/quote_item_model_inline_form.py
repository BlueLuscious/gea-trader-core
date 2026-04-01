""" Form used by the owner quote item inline. """

from typing import Any
from django import forms
from django.forms import ModelChoiceField
from catalog.models import ProductModel, ProductVariantModel
from quotation.models import QuoteItemModel


class QuoteItemModelInlineForm(forms.ModelForm):
    """ Owner-facing form for manually composing quote items before they become snapshots. """

    class Meta:
        model = QuoteItemModel
        fields = ("product", "variant", "quantity", "notes")
        labels = {
            "product": "Product",
            "variant": "Variant",
            "quantity": "Quantity",
            "notes": "Item notes",
        }
        help_texts = {
            "product": "Choose the catalog product this quote item refers to.",
            "variant": "Optional. Choose a specific variant when the quote depends on one.",
            "quantity": "How many units should this quote item include.",
            "notes": "Optional internal note for this specific quote item.",
        }

    def __init__(self, *args, **kwargs) -> None:
        """ Configure owner-friendly field behavior for manual quote item creation.

        Args:
            *args: Positional form arguments.
            **kwargs: Keyword form arguments.
        """
        super().__init__(*args, **kwargs)
        product_field = self.fields.get("product")
        if isinstance(product_field, ModelChoiceField):
            product_field.required = True
            product_field.queryset = ProductModel.objects.active().order_by("name")

        variant_field = self.fields.get("variant")
        if isinstance(variant_field, ModelChoiceField):
            variant_field.required = False
            variant_field.queryset = ProductVariantModel.objects.active().select_related("product").order_by(
                "product_id", "sort_order", "name", "id",
            )

    def clean(self) -> dict[str, Any]:
        """ Validate product and variant consistency for manual quote item creation.

        Returns:
            dict[str, Any]: Cleaned form data.
        """
        cleaned_data = super().clean()
        product: ProductModel | None = cleaned_data.get("product")
        variant: ProductVariantModel | None = cleaned_data.get("variant")

        if product is None:
            return cleaned_data

        if variant is not None and variant.product_id != product.id:
            self.add_error("variant", "The selected variant must belong to the chosen product.")

        return cleaned_data

    def get_selected_product(self) -> ProductModel | None:
        """ Return the selected product from cleaned data when available.

        Returns:
            ProductModel | None: Selected product or ``None``.
        """
        return self.cleaned_data.get("product")

    def get_selected_variant(self) -> ProductVariantModel | None:
        """ Return the selected variant from cleaned data when available.

        Returns:
            ProductVariantModel | None: Selected variant or ``None``.
        """
        return self.cleaned_data.get("variant")

    def is_marked_for_deletion(self) -> bool:
        """ Return whether the inline row is marked for deletion.

        Returns:
            bool: True when the inline row should be deleted.
        """
        return bool(self.cleaned_data.get("DELETE", False))

    def has_selected_product(self) -> bool:
        """ Return whether the inline row contains a selected product.

        Returns:
            bool: True when the inline row contains a selected product.
        """
        return self.get_selected_product() is not None
