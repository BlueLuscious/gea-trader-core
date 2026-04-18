""" Service exports for the accounts app. """

from .owner_delegable_permission_resolver import OwnerDelegablePermissionResolver

__all__: list[str] = ["OwnerDelegablePermissionResolver"]
