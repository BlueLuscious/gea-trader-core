""" Owner-facing tenant settings form. """

from django import forms
from django.utils.translation import gettext_lazy as _
from tenancy.models import TenantModel


class OwnerTenantSettingsForm(forms.ModelForm):
    """ Minimal tenant form used by the owner business settings screen. """

    class Meta:
        """ Declarative configuration for the tenant settings form. """

        model = TenantModel
        fields: tuple[str, ...] = (
            "business_email",
            "support_email",
            "phone_number",
            "website_url",
        )
        labels = {
            "business_email": _("Business email"),
            "support_email": _("Support email"),
            "phone_number": _("Phone number"),
            "website_url": _("Website"),
        }
        help_texts = {
            "business_email": _("Main contact email for this business."),
            "support_email": _("Optional support email shown in emails and messages sent for this business."),
            "phone_number": _("Optional public phone number for this business."),
            "website_url": _("Optional public website URL for this business."),
        }
