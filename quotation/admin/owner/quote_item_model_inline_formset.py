""" Formset used by the owner quote item inline. """

import logging
from typing import Any, TYPE_CHECKING
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _
from quotation.admin.owner.quote_item_model_inline_form import QuoteItemModelInlineForm
from quotation.models import QuoteItemModel

if TYPE_CHECKING:
    from quotation.models import QuoteModel

logger = logging.getLogger(__name__)


class QuoteItemModelInlineFormSet(BaseInlineFormSet):
    """ Build quote item snapshots from owner-entered product and variant selections. """

    instance: "QuoteModel"

    def _get_valid_bound_forms(self) -> list[QuoteItemModelInlineForm]:
        """ Return bound inline forms that already passed validation.

        Returns:
            list[QuoteItemModelInlineForm]: Valid bound quote item inline forms.
        """
        return [
            form
            for form in self.forms
            if isinstance(form, QuoteItemModelInlineForm) and form.is_bound and form.is_valid()
        ]

    def clean(self) -> None:
        """ Ensure manual quotes contain at least one non-deleted item.

        Raises:
            ValidationError: When the owner tries to save a quote without items.
        """
        super().clean()

        has_item = any(
            form.has_selected_product()
            for form in self._get_valid_bound_forms()
            if not form.is_marked_for_deletion()
        )

        if not has_item and self.instance.pk is None:
            raise ValidationError(_("Add at least one quote item before saving the quote."))

    def get_form_kwargs(self, index: int) -> dict[str, Any]:
        """ Return form kwargs enriched with the active tenant context.

        Args:
            index: Position of the inline form in the formset.

        Returns:
            dict[str, Any]: Form keyword arguments with tenant context when available.
        """
        kwargs = super().get_form_kwargs(index)
        kwargs["tenant"] = getattr(self.instance, "tenant", None)
        return kwargs

    def save_new(self, form: QuoteItemModelInlineForm, commit: bool = True) -> QuoteItemModel:
        """ Populate snapshot fields for a newly created quote item.

        Args:
            form: Inline form containing product and optional variant selections.
            commit: Whether to persist the instance immediately.

        Returns:
            QuoteItemModel: Newly created quote item with snapshot fields populated.
        """
        instance: QuoteItemModel = super().save_new(form, commit=False)
        product = form.get_selected_product()
        variant = form.get_selected_variant()

        if product is None:
            raise ValidationError(_("Quote items require a selected product."))

        instance.product_name_snapshot = product.name
        instance.sku_snapshot = variant.sku if variant is not None else product.sku_base
        instance.attributes_snapshot = dict(variant.attributes_json or {}) if variant is not None else {}
        instance.unit_price_snapshot = variant.price if variant is not None else None

        logger.info(
            "Built owner quote item snapshot tenant_id=%s quote_id=%s product_id=%s variant_id=%s",
            getattr(self.instance, "tenant_id", None),
            getattr(self.instance, "pk", None),
            product.pk,
            getattr(variant, "pk", None),
        )

        if commit:
            instance.save()
            form.save_m2m()

        return instance
