""" Mail DTO exports. """

from core.mail.dtos.mail_attachment_dto import MailAttachmentDTO
from core.mail.dtos.mail_message_dto import MailMessageDTO
from core.mail.dtos.mail_recipient_dto import MailRecipientDTO
from core.mail.dtos.template_mail_request_dto import TemplateMailRequestDTO

__all__: list[str] = [
    "MailAttachmentDTO",
    "MailMessageDTO",
    "MailRecipientDTO",
    "TemplateMailRequestDTO",
]
