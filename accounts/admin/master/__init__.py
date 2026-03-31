""" Master admin registrations for the accounts app. """

from .group_admin import GroupAdmin
from .user_model_admin import UserModelAdmin

__all__: list[str] = ["GroupAdmin", "UserModelAdmin"]
