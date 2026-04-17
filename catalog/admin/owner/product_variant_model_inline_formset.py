""" Owner inline formset for product variants. """

from typing import Any
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _


class ProductVariantModelInlineFormSet(BaseInlineFormSet):
    """ Enforce one complete default-variant contract on owner product saves. """

    def _is_submitted_variant_form(self, form: ModelForm) -> bool:
        """ Return whether one inline row contains variant data to keep.

        Args:
            form: Inline product-variant form.

        Returns:
            bool: ``True`` when the row is persisted already or includes posted data.
        """
        if form.instance.pk is not None:
            return True

        submitted_values = (
            form.data.get(form.add_prefix("name"), ""),
            form.data.get(form.add_prefix("sku"), ""),
            form.data.get(form.add_prefix("price"), ""),
            form.data.get(form.add_prefix("sort_order"), ""),
            form.data.get(form.add_prefix("is_default"), ""),
            form.data.get(form.add_prefix("is_active"), ""),
        )
        return any(str(value).strip() for value in submitted_values)

    def _get_submitted_variant_forms(self) -> list[ModelForm]:
        """ Return submitted or persisted variant forms that stay in the product.

        Returns:
            list[ModelForm]: Submitted or persisted, non-deleted inline variant forms.
        """
        return [
            form
            for form in self.forms
            if form.is_bound
            and not form.errors
            and self._is_submitted_variant_form(form)
            and not self._should_delete_form(form)
        ]

    def _is_default_variant_form(self, form: ModelForm) -> bool:
        """ Return whether one submitted row is marked as the default variant.

        Args:
            form: Inline product-variant form.

        Returns:
            bool: ``True`` when the submitted row is marked as default.
        """
        return bool(form.data.get(form.add_prefix("is_default")))

    def _requires_quote(self) -> bool:
        """ Return whether the parent product still follows the quote-only flow.

        Returns:
            bool: ``True`` when the owner submitted or kept quote-only behavior.
        """
        if self.is_bound:
            return bool(self.data.get("requires_quote"))

        return bool(getattr(self.instance, "requires_quote", False))

    def get_form_kwargs(self, index: int) -> dict[str, Any]:
        """ Pass current product quote behavior into each inline form.

        Args:
            index: Position of the inline form inside the formset.

        Returns:
            dict[str, Any]: Inline form kwargs enriched with quote behavior context.
        """
        kwargs = super().get_form_kwargs(index)
        kwargs["requires_quote"] = self._requires_quote()
        return kwargs

    def _has_price(self, form: ModelForm) -> bool:
        """ Return whether one inline variant row currently carries a usable price.

        Args:
            form: Inline product-variant form.

        Returns:
            bool: ``True`` when the row keeps or submits a price.
        """
        if hasattr(form, "cleaned_data") and form.cleaned_data.get("price") is not None:
            return True

        submitted_price = str(form.data.get(form.add_prefix("price"), "")).strip()
        if submitted_price:
            return True

        return getattr(form.instance, "price", None) is not None

    def clean(self) -> None:
        """ Require a complete default variant contract for the current product flow.

        Raises:
            ValidationError: When the submitted inline variants do not satisfy the
                default-variant contract.
        """
        super().clean()

        variant_forms = self._get_submitted_variant_forms()
        if not variant_forms:
            raise ValidationError(_("Add at least one variant before saving the product."))

        default_variant_forms = [
            form
            for form in variant_forms
            if self._is_default_variant_form(form)
        ]
        default_variant_count = len(default_variant_forms)
        if default_variant_count != 1:
            raise ValidationError(_("Choose exactly one default variant for this product."))

        if not self._requires_quote():
            if not self._has_price(default_variant_forms[0]):
                raise ValidationError(_("Purchasable products require a price on the default variant."))
