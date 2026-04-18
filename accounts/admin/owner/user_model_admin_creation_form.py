""" Form used by the owner user admin add view. """

from django import forms
from django.utils.translation import gettext_lazy as _
from unfold.forms import UserCreationForm
from accounts.models import UserModel


class OwnerUserModelAdminCreationForm(UserCreationForm):
    """ Owner-facing form for creating support user accounts. """

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=_("Set a temporary password for this team account."),
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=_("Type the same password again to confirm it."),
    )
    
    class Meta(UserCreationForm.Meta):
        """ Declarative field presentation for owner user creation. """

        model = UserModel
        fields = ("username", "first_name", "last_name", "email", "is_active", "is_staff", "groups")
        labels = {
            "username": _("Username"),
            "first_name": _("First name"),
            "last_name": _("Last name"),
            "email": _("Email"),
            "is_active": _("Active"),
            "is_staff": _("Can open business admin"),
            "groups": _("Groups"),
        }
        help_texts = {
            "email": _("Use a real contact email for notifications and password recovery."),
            "is_active": _("Disable this user instead of deleting the account."),
            "is_staff": _("Keep this enabled so this person can open the business admin."),
            "groups": _("Only permission groups for the current business can be assigned here."),
        }

    def __init__(self, *args, **kwargs) -> None:
        """ Set owner-friendly defaults for newly created support users.

        Args:
            *args: Positional form arguments.
            **kwargs: Keyword form arguments.
        """
        super().__init__(*args, **kwargs)
        
        self.fields["is_active"].initial = True
        self.fields["is_staff"].initial = True
