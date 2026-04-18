""" Inline form used by the owner tenant-branding screen. """

from django import forms
from tenancy.models import TenantBrandingModel


class TenantBrandingInlineForm(forms.ModelForm):
    """ Owner-facing inline form for one tenant branding record. """

    class Meta:
        """ Declarative presentation for the branding inline form. """

        model = TenantBrandingModel
        fields = (
            "display_name",
            "logo_light",
            "logo_dark",
            "icon_light",
            "icon_dark",
            "favicon_light",
            "favicon_dark",
        )
