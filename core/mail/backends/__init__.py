""" Mail delivery backend exports. """

from core.mail.backends.django_mail_delivery_backend import DjangoMailDeliveryBackend

__all__: list[str] = ["DjangoMailDeliveryBackend"]
