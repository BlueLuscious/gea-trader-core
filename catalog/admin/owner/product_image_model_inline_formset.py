""" Owner inline formset for product images. """

import logging
from typing import TYPE_CHECKING
from django.forms import BaseForm, ModelChoiceField
from django.forms.models import BaseInlineFormSet
from catalog.models import ProductVariantModel

if TYPE_CHECKING:
    from catalog.models import ProductModel

logger = logging.getLogger(__name__)


class ProductImageModelInlineFormSet(BaseInlineFormSet):
    """ Restrict image inline variant choices to variants of the current product. """

    def add_fields(self, form: BaseForm, index: int | None) -> None:
        """ Add form fields and limit the variant queryset to the parent product.

        Args:
            form: Inline admin form instance.
            index: Zero-based position of the form inside the formset.
        """
        super().add_fields(form, index)

        if "variant" not in form.fields:
            return

        variant_field = form.fields["variant"]
        if not isinstance(variant_field, ModelChoiceField):
            return

        product: "ProductModel" = self.instance
        if product.pk is None:
            variant_field.queryset = ProductVariantModel.objects.none()
            logger.info("Built owner product image variant field without a persisted product")
            return

        variant_queryset = ProductVariantModel.objects.filter(
            product=product,
        ).order_by("sort_order", "name", "id")
        variant_field.queryset = variant_queryset
        logger.info(
            "Built owner product image variant field product_id=%s variant_count=%s",
            product.pk,
            variant_queryset.count(),
        )
