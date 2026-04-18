""" Base contract for active-tenant resolution strategies. """

from abc import ABC, abstractmethod
from django.http import HttpRequest
from tenancy.models import TenantModel


class TenantResolutionStrategy(ABC):
    """ Define the contract for one request-time tenant resolution strategy. """

    @classmethod
    @abstractmethod
    def resolve(cls, request: HttpRequest) -> TenantModel | None:
        """ Attempt to resolve one tenant for the current request.

        Args:
            request: Current HTTP request.

        Returns:
            TenantModel | None: Resolved tenant when the strategy applies.
        """
        raise NotImplementedError
