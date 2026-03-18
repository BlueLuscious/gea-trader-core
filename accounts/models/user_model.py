""" Custom user model for the accounts app. """

from django.contrib.auth.models import AbstractUser
from accounts.models.managers.user_model_manager import UserModelManager


class UserModel(AbstractUser):
    """ Base user model used by Django auth within this project. """

    objects: UserModelManager = UserModelManager()
