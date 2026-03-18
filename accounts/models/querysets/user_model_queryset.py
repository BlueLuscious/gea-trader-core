""" Reusable queryset helpers for the user model. """

from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from accounts.models.user_model import UserModel


class UserModelQuerySet(models.QuerySet["UserModel"]):
    """ QuerySet for reusable user filters. """
