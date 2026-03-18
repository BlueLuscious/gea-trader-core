""" Custom manager for the user model. """

from typing import TYPE_CHECKING
from django.contrib.auth.models import UserManager
from accounts.models.querysets.user_model_queryset import UserModelQuerySet

if TYPE_CHECKING:
    from accounts.models.user_model import UserModel


class UserModelManager(UserManager["UserModel"]):
    """ Manager exposing Django auth behavior plus typed user queryset helpers. """

    def get_queryset(self) -> UserModelQuerySet:
        """ Return the base queryset for user queries.

        Returns:
            UserModelQuerySet: A specialized queryset for UserModel.
        """
        return UserModelQuerySet(self.model, using=self._db)
