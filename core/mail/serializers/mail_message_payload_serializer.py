""" Serialize outbound mail message DTOs into Celery-safe payloads. """

from collections.abc import Mapping
from typing import Any
from core.mail.dtos import MailAttachmentDTO, MailMessageDTO, MailRecipientDTO


class MailMessagePayloadSerializer:
    """ Convert raw mail DTOs to and from plain Celery-safe payload dictionaries. """

    @classmethod
    def serialize(cls, message: MailMessageDTO) -> dict[str, Any]:
        """ Serialize one outbound mail message DTO.

        Args:
            message: Outbound mail message DTO.

        Returns:
            dict[str, Any]: Plain serialized payload suitable for Celery transport.
        """
        return {
            "subject": message.subject,
            "to": [cls._serialize_recipient(recipient) for recipient in message.to],
            "text_body": message.text_body,
            "html_body": message.html_body,
            "from_email": message.from_email,
            "cc": [cls._serialize_recipient(recipient) for recipient in message.cc],
            "bcc": [cls._serialize_recipient(recipient) for recipient in message.bcc],
            "reply_to": list(message.reply_to),
            "headers": dict(message.headers),
            "attachments": [cls._serialize_attachment(attachment) for attachment in message.attachments],
        }

    @classmethod
    def deserialize(cls, payload: Mapping[str, Any]) -> MailMessageDTO:
        """ Deserialize one plain payload into one outbound mail message DTO.

        Args:
            payload: Serialized mail message payload.

        Returns:
            MailMessageDTO: Rebuilt outbound mail message DTO.
        """
        return MailMessageDTO(
            subject=str(payload["subject"]),
            to=[cls._deserialize_recipient(item) for item in payload["to"]],
            text_body=str(payload["text_body"]),
            html_body=str(payload["html_body"]) if payload.get("html_body") is not None else None,
            from_email=str(payload["from_email"]) if payload.get("from_email") is not None else None,
            cc=[cls._deserialize_recipient(item) for item in payload.get("cc", [])],
            bcc=[cls._deserialize_recipient(item) for item in payload.get("bcc", [])],
            reply_to=tuple(str(address) for address in payload.get("reply_to", [])),
            headers={str(key): str(value) for key, value in dict(payload.get("headers", {})).items()},
            attachments=[cls._deserialize_attachment(item) for item in payload.get("attachments", [])],
        )

    @staticmethod
    def _serialize_recipient(recipient: MailRecipientDTO) -> dict[str, str | None]:
        """ Serialize one recipient DTO.

        Args:
            recipient: Recipient DTO to serialize.

        Returns:
            dict[str, str | None]: Plain recipient payload.
        """
        return {
            "email": recipient.email,
            "name": recipient.name,
        }

    @staticmethod
    def _deserialize_recipient(payload: Mapping[str, Any]) -> MailRecipientDTO:
        """ Deserialize one recipient payload.

        Args:
            payload: Plain recipient payload.

        Returns:
            MailRecipientDTO: Rebuilt recipient DTO.
        """
        return MailRecipientDTO(
            email=str(payload["email"]),
            name=str(payload["name"]) if payload.get("name") is not None else None,
        )

    @staticmethod
    def _serialize_attachment(attachment: MailAttachmentDTO) -> dict[str, Any]:
        """ Serialize one attachment DTO.

        Args:
            attachment: Attachment DTO to serialize.

        Returns:
            dict[str, Any]: Plain attachment payload.
        """
        return {
            "filename": attachment.filename,
            "content": attachment.content,
            "mimetype": attachment.mimetype,
        }

    @staticmethod
    def _deserialize_attachment(payload: Mapping[str, Any]) -> MailAttachmentDTO:
        """ Deserialize one attachment payload.

        Args:
            payload: Plain attachment payload.

        Returns:
            MailAttachmentDTO: Rebuilt attachment DTO.
        """
        return MailAttachmentDTO(
            filename=str(payload["filename"]),
            content=payload["content"],
            mimetype=str(payload["mimetype"]) if payload.get("mimetype") is not None else None,
        )
