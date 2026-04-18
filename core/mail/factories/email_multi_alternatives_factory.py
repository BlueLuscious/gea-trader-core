""" Factory that builds Django outbound email objects from DTOs. """

from collections.abc import Sequence
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend
from core.mail.dtos import MailMessageDTO, MailRecipientDTO


class EmailMultiAlternativesFactory:
    """ Build ``EmailMultiAlternatives`` instances from mail DTOs. """

    @classmethod
    def build(cls, message: MailMessageDTO, connection: BaseEmailBackend | None = None) -> EmailMultiAlternatives:
        """ Build one Django email object from one outbound message DTO.

        Args:
            message: Outbound mail payload.
            connection: Optional Django mail backend connection.

        Returns:
            EmailMultiAlternatives: Configured Django email object.
        """
        email_message = EmailMultiAlternatives(
            subject=message.subject,
            body=message.text_body,
            from_email=message.from_email or settings.DEFAULT_FROM_EMAIL,
            to=cls._build_address_list(message.to),
            cc=cls._build_address_list(message.cc),
            bcc=cls._build_address_list(message.bcc),
            reply_to=list(message.reply_to),
            headers=dict(message.headers),
            connection=connection,
        )

        if message.html_body:
            email_message.attach_alternative(message.html_body, "text/html")

        for attachment in message.attachments:
            email_message.attach(attachment.filename, attachment.content, attachment.mimetype)

        return email_message

    @staticmethod
    def _build_address_list(recipients: Sequence[MailRecipientDTO]) -> list[str]:
        """ Convert one recipient sequence into a Django-compatible address list.

        Args:
            recipients: Recipients to format.

        Returns:
            list[str]: RFC 822 formatted recipient addresses.
        """
        return [recipient.as_rfc822_address() for recipient in recipients]
