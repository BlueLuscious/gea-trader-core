""" Inline formset used by the owner tenant-branding screen. """

from django.forms.models import BaseInlineFormSet


class TenantBrandingInlineFormSet(BaseInlineFormSet):
    """ Inline formset used by the native owner tenant change form. """
