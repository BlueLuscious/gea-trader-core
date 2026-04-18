""" Owner admin registrations for the accounts app. """

from .group_admin import OwnerGroupAdmin
from .user_model_admin import OwnerUserModelAdmin

__all__: list[str] = ["OwnerGroupAdmin", "OwnerUserModelAdmin"]
