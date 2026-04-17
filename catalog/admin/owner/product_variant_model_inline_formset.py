""" Owner inline formset for product variants. """

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

    def clean(self) -> None:
        """ Require at least one variant and exactly one default variant.

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
