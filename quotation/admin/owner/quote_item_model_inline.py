""" Owner inline admin for quote items. """

from typing import Any, TYPE_CHECKING
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from unfold.admin import StackedInline
from quotation.admin.owner.quote_item_model_inline_form import QuoteItemModelInlineForm
from quotation.admin.owner.quote_item_model_inline_formset import QuoteItemModelInlineFormSet
from quotation.models import QuoteItemModel

if TYPE_CHECKING:
    from quotation.models.quote_model import QuoteModel


class QuoteItemModelInline(StackedInline):
    """ Read-only inline view of quote item snapshots inside the owner quote admin. """

    model = QuoteItemModel
    form = QuoteItemModelInlineForm
    formset = QuoteItemModelInlineFormSet
    tab = True
    show_count = True
    can_delete = False
    show_change_link = False
    verbose_name = _("Quote item")
    verbose_name_plural = _("Quote items")

    def get_fields(self, request: HttpRequest, obj: "QuoteModel | None" = None) -> tuple[Any, ...]:
        """ Return add-time or read-only fields depending on quote persistence state.

        Args:
            request: Current admin request.
            obj: Parent quote instance when available.

        Returns:
            tuple[Any, ...]: Inline field layout for the current owner workflow stage.
        """
        if obj is None:
            return (
                ("product", "variant"),
                ("quantity", "notes"),
            )

        return (
            ("product_name_snapshot", "sku_snapshot"),
            ("unit_price_snapshot", "quantity"),
            "attributes_snapshot",
            "notes",
            "created_at",
        )

    def get_readonly_fields(self, request: HttpRequest, obj: "QuoteModel | None" = None) -> tuple[str, ...]:
        """ Freeze quote item snapshots once the parent quote has been created.

        Args:
            request: Current admin request.
            obj: Parent quote instance when available.

        Returns:
            tuple[str, ...]: Read-only fields for the current owner workflow stage.
        """
        if obj is None:
            return ()

        return (
            "product_name_snapshot",
            "sku_snapshot",
            "attributes_snapshot",
            "unit_price_snapshot",
            "quantity",
            "notes",
            "created_at",
        )

    def get_extra(self, request: HttpRequest, obj: "QuoteModel | None" = None, **kwargs: Any) -> int:
        """ Show one empty row while creating a quote and none afterwards.

        Args:
            request: Current admin request.
            obj: Parent quote instance when available.
            **kwargs: Extra inline admin keyword arguments.

        Returns:
            int: Number of extra inline rows.
        """
        return 1 if obj is None else 0

    def has_add_permission(self, request: HttpRequest, obj: "QuoteModel | None" = None) -> bool:
        """ Allow quote items only while manually creating a new quote.

        Args:
            request: Current admin request.
            obj: Parent quote instance when available.

        Returns:
            bool: True only on the add flow before the quote exists.
        """
        return obj is None
