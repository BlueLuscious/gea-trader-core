""" Owner-facing form for brand administration. """

from django import forms
from django.utils.translation import gettext_lazy as _
from masterdata.models import BrandModel


class BrandModelAdminForm(forms.ModelForm):
    """ Owner-facing form for one brand record. """

    class Meta:
        """ Configure the form for the owner brand admin. """

        model = BrandModel
        fields = "__all__"
        labels = {
            "name": _("Brand name"),
            "slug": _("URL slug"),
            "description": _("Description"),
            "is_active": _("Available for products"),
        }
        help_texts = {
            "slug": _("Usually created from the brand name. Adjust it only when you need a custom URL."),
            "description": _("Optional. Add short internal guidance about when this brand should be used."),
            "is_active": _("Disable this brand when you want to stop using it without deleting its history."),
        }
