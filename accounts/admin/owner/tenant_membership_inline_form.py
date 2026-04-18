""" Form used by the owner user admin tenant membership inline. """

from django import forms
from django.utils.translation import gettext_lazy as _
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel


class TenantMembershipInlineForm(forms.ModelForm):
    """ Owner-facing form for one tenant-scoped user membership. """

    class Meta:
        """ Declarative field presentation for owner membership editing. """

        model = TenantMembershipModel
        fields = ("role", "is_active")
        labels = {
            "role": _("Business role"),
            "is_active": _("Access active"),
        }
        help_texts = {
            "role": _("Choose whether this person manages this business or works on the team."),
            "is_active": _("Turn off access to this business without deleting the user."),
        }

    def __init__(self, *args, **kwargs) -> None:
        """ Limit editable tenant roles to owner-managed options.

        Args:
            *args: Positional form arguments.
            **kwargs: Keyword form arguments.
        """
        super().__init__(*args, **kwargs)
        
        role_field = self.fields.get("role")
        if role_field is not None:
            role_field.initial = TenantRole.OPERATOR
            role_field.choices = [
                (TenantRole.OWNER, TenantRole.OWNER.label),
                (TenantRole.OPERATOR, TenantRole.OPERATOR.label),
            ]

        is_active_field = self.fields.get("is_active")
        if is_active_field is not None:
            is_active_field.initial = True
