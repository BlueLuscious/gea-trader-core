""" Django-backed outbound mail delivery backend. """

from collections.abc import Sequence
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend
from core.mail.factories import EmailMultiAlternativesFactory
from core.mail.dtos import MailMessageDTO


class DjangoMailDeliveryBackend:
    """ Send outbound mail through Django's configured email backend. """

    factory_class = EmailMultiAlternativesFactory

    @classmethod
    def send(cls, message: MailMessageDTO, fail_silently: bool = False) -> int:
        """ Send one outbound message through the configured Django backend.

        Args:
            message: Outbound mail payload.
            fail_silently: Whether the backend should swallow transport errors.

        Returns:
            int: Number of successfully delivered messages.
        """
        email_message = cls.factory_class.build(message)
        return email_message.send(fail_silently=fail_silently)

    @classmethod
    def send_many(cls, messages: Sequence[MailMessageDTO], fail_silently: bool = False) -> int:
        """ Send multiple outbound messages through one shared backend connection.

        Args:
            messages: Outbound mail payloads.
            fail_silently: Whether the backend should swallow transport errors.

        Returns:
            int: Number of successfully delivered messages.
        """
        if not messages:
            return 0

        connection: BaseEmailBackend = get_connection(fail_silently=fail_silently)
        email_messages = [
            cls.factory_class.build(message, connection=connection)
            for message in messages
        ]
        return connection.send_messages(email_messages)
