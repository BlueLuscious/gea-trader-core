""" Form used by the owner user admin change view. """

from django.utils.translation import gettext_lazy as _
from unfold.forms import UserChangeForm
from accounts.models import UserModel


class OwnerUserModelAdminForm(UserChangeForm):
    """ Owner-facing form for editing support user accounts. """

    class Meta(UserChangeForm.Meta):
        """ Declarative field presentation for owner user editing. """

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
