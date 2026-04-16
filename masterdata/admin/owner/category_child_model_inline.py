""" Owner inline admin for direct category children. """

from typing import Any
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline
from masterdata.access import CategoryAccessPolicy
from masterdata.admin.owner.category_child_model_inline_form import CategoryChildModelInlineForm
from masterdata.admin.owner.category_child_model_inline_formset import CategoryChildModelInlineFormSet
from masterdata.models import CategoryModel


class CategoryChildModelInline(TabularInline):
    """ Inline editor for direct child categories inside the owner category admin. """

    model = CategoryModel
    fk_name = "parent"
    form = CategoryChildModelInlineForm
    formset = CategoryChildModelInlineFormSet
    tab = True
    show_count = True
    show_change_link = True
    can_delete = False
    extra = 0
    ordering = ("sort_order", "name", "id")
    prepopulated_fields = {"slug": ("name",)}
    verbose_name = _("Subcategory")
    verbose_name_plural = _("Subcategories")

    def get_extra(self, request: HttpRequest, obj: CategoryModel | None = None, **kwargs: Any) -> int:
        """ Show one empty child row only when editing an existing parent category.

        Args:
            request: Current admin request.
            obj: Parent category instance when available.
            **kwargs: Extra inline admin keyword arguments.

        Returns:
            int: Number of empty child rows to render.
        """
        return 1

    def has_add_permission(self, request: HttpRequest, obj: CategoryModel | None = None) -> bool:
        """ Allow child-category creation only on change views with add permission.

        Args:
            request: Current admin request.
            obj: Parent category instance when available.

        Returns:
            bool: ``True`` when the current request may add categories.
        """
        return CategoryAccessPolicy.can_add_category(request)
