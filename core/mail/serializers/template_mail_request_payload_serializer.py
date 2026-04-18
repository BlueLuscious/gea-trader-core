""" Serialize templated mail request DTOs into Celery-safe payloads. """

from collections.abc import Mapping
from typing import Any
from core.mail.dtos import MailAttachmentDTO, MailRecipientDTO, TemplateMailRequestDTO
from core.mail.resolvers import MailTemplateBaseContextBuilder


class TemplateMailRequestPayloadSerializer:
    """ Convert templated mail request DTOs to and from plain Celery-safe payload dictionaries. """

    base_context_builder_class = MailTemplateBaseContextBuilder

    @classmethod
    def serialize(cls, request: TemplateMailRequestDTO) -> dict[str, Any]:
        """ Serialize one templated mail request DTO.

        Args:
            request: Templated mail request DTO.

        Returns:
            dict[str, Any]: Plain serialized payload suitable for Celery transport.
        """
        return {
            "subject": request.subject,
            "to": [cls._serialize_recipient(recipient) for recipient in request.to],
            "context": cls._serialize_context(request),
            "html_template_name": request.html_template_name,
            "text_template_name": request.text_template_name,
            "from_email": request.from_email,
            "cc": [cls._serialize_recipient(recipient) for recipient in request.cc],
            "bcc": [cls._serialize_recipient(recipient) for recipient in request.bcc],
            "reply_to": list(request.reply_to),
            "headers": dict(request.headers),
            "attachments": [cls._serialize_attachment(attachment) for attachment in request.attachments],
        }

    @classmethod
    def deserialize(cls, payload: Mapping[str, Any]) -> TemplateMailRequestDTO:
        """ Deserialize one plain payload into one templated mail request DTO.

        Args:
            payload: Serialized templated mail request payload.

        Returns:
            TemplateMailRequestDTO: Rebuilt templated mail request DTO.
        """
        return TemplateMailRequestDTO(
            subject=str(payload["subject"]),
            to=[cls._deserialize_recipient(item) for item in payload["to"]],
            context=dict(payload["context"]),
            html_template_name=str(payload["html_template_name"]),
            text_template_name=str(payload["text_template_name"]),
            tenant=None,
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

    @classmethod
    def _serialize_context(cls, request: TemplateMailRequestDTO) -> dict[str, Any]:
        """ Serialize one request context together with its tenant-aware base snapshot.

        Args:
            request: Templated mail request DTO.

        Returns:
            dict[str, Any]: Context snapshot ready for asynchronous rendering.
        """
        return cls.base_context_builder_class.build(
            context=request.context,
            tenant=request.tenant,
        )
