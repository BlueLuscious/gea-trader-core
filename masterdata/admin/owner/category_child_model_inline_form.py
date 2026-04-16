""" Owner-facing inline form for direct child categories. """

from django import forms
from django.utils.translation import gettext_lazy as _
from masterdata.models import CategoryModel


class CategoryChildModelInlineForm(forms.ModelForm):
    """ Compact owner-facing form for direct child categories. """

    class Meta:
        """ Configure the inline form for child-category editing. """

        model = CategoryModel
        fields = (
            "name",
            "slug",
            "sort_order",
            "is_active",
        )
        labels = {
            "name": _("Subcategory name"),
            "slug": _("URL slug"),
            "sort_order": _("Display order"),
            "is_active": _("Available for products"),
        }
        help_texts = {
            "slug": _("Usually created from the subcategory name. Adjust it only when you need a custom URL."),
            "sort_order": _("Lower values appear first inside this parent category."),
        }
