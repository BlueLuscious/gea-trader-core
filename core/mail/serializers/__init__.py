""" Public serializer exports for the mail package. """

from core.mail.serializers.mail_message_payload_serializer import MailMessagePayloadSerializer
from core.mail.serializers.template_mail_request_payload_serializer import TemplateMailRequestPayloadSerializer

__all__: list[str] = [
    "MailMessagePayloadSerializer",
    "TemplateMailRequestPayloadSerializer",
]
