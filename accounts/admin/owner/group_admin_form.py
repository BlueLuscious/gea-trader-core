""" Form used by the owner group admin. """

from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _


class OwnerGroupAdminForm(forms.ModelForm):
    """ Owner-facing form for tenant-scoped support groups. """

    class Meta:
        """ Declarative field presentation for owner group editing. """

        model = Group
        fields = ("name", "permissions")
        labels = {
            "name": _("Group name"),
            "permissions": _("Granted permissions"),
        }
        help_texts = {
            "name": _("Use a clear name that describes what this team group is for."),
            "permissions": _("People in this group will receive the permissions selected here."),
        }
