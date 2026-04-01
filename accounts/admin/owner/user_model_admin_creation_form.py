""" Form used by the owner user admin add view. """

from django import forms
from unfold.forms import UserCreationForm
from accounts.models import UserModel


class OwnerUserModelAdminCreationForm(UserCreationForm):
    """ Owner-facing form for creating support user accounts. """

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Set an initial password for this support account.",
    )
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Re-enter the same password to confirm it.",
    )

    class Meta(UserCreationForm.Meta):
        """ Declarative field presentation for owner user creation. """

        model = UserModel
        fields = ("username", "first_name", "last_name", "email", "is_active", "is_staff")
        labels = {
            "username": "Username",
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email",
            "is_active": "Active",
            "is_staff": "Can access owner admin",
        }
        help_texts = {
            "email": "Use a real contact address for support and password recovery.",
            "is_active": "Disable this user instead of deleting the account.",
            "is_staff": "Keep this enabled so the user can access the owner administration site.",
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
