""" Admin site namespaces used across the project. """

from enum import StrEnum


class AdminNamespace(StrEnum):
    """ Supported admin site namespaces. """

    MASTER = "master_admin"
    OWNER = "owner_admin"
