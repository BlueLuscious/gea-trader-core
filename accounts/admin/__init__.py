""" Accounts admin package. """

from accounts.admin.owner import OwnerGroupAdmin, OwnerUserModelAdmin
from accounts.admin.master import GroupAdmin, UserModelAdmin

__all__: list[str] = ["GroupAdmin", "OwnerGroupAdmin", "OwnerUserModelAdmin", "UserModelAdmin"]
