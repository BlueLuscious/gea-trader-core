""" Form used by the owner quote item inline. """

from typing import Any
from django import forms
from django.forms import ModelChoiceField
from catalog.models import ProductModel, ProductVariantModel
from quotation.models import QuoteItemModel
from tenancy.models import TenantModel


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
        tenant: TenantModel | None = kwargs.pop("tenant", None)
        super().__init__(*args, **kwargs)
        self._configure_product_field(tenant)
        self._configure_variant_field(tenant)

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

    def _configure_product_field(self, tenant: TenantModel | None) -> None:
        """ Configure the tenant-scoped product field queryset.

        Args:
            tenant: Active tenant in scope for the owner quote flow.
        """
        product_field = self.fields.get("product")
        if not isinstance(product_field, ModelChoiceField):
            return

        product_field.required = True
        product_queryset = ProductModel.objects.active()
        if tenant is not None:
            product_queryset = product_queryset.for_tenant(tenant)

        product_field.queryset = product_queryset.order_by("name")

    def _configure_variant_field(self, tenant: TenantModel | None) -> None:
        """ Configure the tenant-scoped variant field queryset.

        Args:
            tenant: Active tenant in scope for the owner quote flow.
        """
        variant_field = self.fields.get("variant")
        if not isinstance(variant_field, ModelChoiceField):
            return

        variant_field.required = False
        variant_queryset = ProductVariantModel.objects.active().select_related("product")
        if tenant is not None:
            variant_queryset = variant_queryset.for_tenant(tenant)

        variant_field.queryset = variant_queryset.order_by(
            "product_id", "sort_order", "name", "id",
        )
