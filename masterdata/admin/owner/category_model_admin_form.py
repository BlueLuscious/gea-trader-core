""" Owner-facing form for category administration. """

from django.http import HttpRequest
from django import forms
from django.utils.translation import gettext_lazy as _
from masterdata.models import CategoryModel


class CategoryModelAdminForm(forms.ModelForm):
    """ Owner-facing form for one category record. """

    request: HttpRequest | None

    def __init__(self, *args: object, request: HttpRequest | None = None, **kwargs: object) -> None:
        """ Bind the active tenant to the category instance before validation.

        Args:
            *args: Positional form arguments.
            request: Current admin request.
            **kwargs: Keyword form arguments.
        """
        super().__init__(*args, **kwargs)
        self.request = request

        active_tenant = getattr(request, "tenant", None)
        if active_tenant is not None:
            self.instance.tenant = active_tenant

    class Meta:
        """ Configure the form for the owner category admin. """

        model = CategoryModel
        fields = "__all__"
        labels = {
            "name": _("Category name"),
            "slug": _("URL slug"),
            "description": _("Description"),
            "parent": _("Parent category"),
            "sort_order": _("Display order"),
            "is_active": _("Available for products"),
        }
        help_texts = {
            "slug": _("Usually created from the category name. Adjust it only when you need a custom URL."),
            "description": _("Optional. Add short guidance so your team understands when to use this category."),
            "parent": _("Optional. Leave empty to keep this category at the root level of the business catalog."),
            "sort_order": _("Lower values appear first when categories are listed."),
            "is_active": _("Disable this category when you want to stop offering it without deleting its history."),
        }
