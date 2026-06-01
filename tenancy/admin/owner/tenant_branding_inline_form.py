""" Inline form used by the owner tenant-branding screen. """

from django import forms
from django.utils.translation import gettext_lazy as _
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
            "instagram_url",
            "facebook_url",
            "linkedin_url",
        )
        labels = {
            "display_name": _("Public display name"),
            "logo_light": _("Light logo"),
            "logo_dark": _("Dark logo"),
            "icon_light": _("Light icon"),
            "icon_dark": _("Dark icon"),
            "favicon_light": _("Light favicon"),
            "favicon_dark": _("Dark favicon"),
            "instagram_url": _("Instagram URL"),
            "facebook_url": _("Facebook URL"),
            "linkedin_url": _("LinkedIn URL"),
        }
        help_texts = {
            "display_name": _("Optional name shown on public and admin surfaces instead of the business name."),
            "logo_light": _("Logo for light backgrounds, such as light storefront sections or emails."),
            "logo_dark": _("Logo for dark backgrounds, such as dark storefront sections or admin chrome."),
            "icon_light": _("Compact icon for light backgrounds when a full logo would be too large."),
            "icon_dark": _("Compact icon for dark backgrounds when a full logo would be too large."),
            "favicon_light": _("Browser icon variant intended for light browser themes."),
            "favicon_dark": _("Browser icon variant intended for dark browser themes."),
            "instagram_url": _("Optional public Instagram profile shown on contact surfaces."),
            "facebook_url": _("Optional public Facebook page shown on contact surfaces."),
            "linkedin_url": _("Optional public LinkedIn profile or company page shown on contact surfaces."),
        }
