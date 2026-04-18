""" Public mail package exports. """

from core.mail.composers import TemplateMailComposer
from core.mail.dtos import MailAttachmentDTO, MailMessageDTO, MailRecipientDTO, TemplateMailRequestDTO
from core.mail.policies import SystemMailSenderPolicy, TenantMailReplyPolicy
from core.mail.resolvers import TenantMailContextResolver, TenantMailRecipientResolver
from core.mail.serializers import MailMessagePayloadSerializer, TemplateMailRequestPayloadSerializer
from core.mail.services import MailService, TemplateMailService

__all__: list[str] = [
    "TemplateMailComposer",
    "MailAttachmentDTO",
    "MailMessageDTO",
    "MailRecipientDTO",
    "TemplateMailRequestDTO",
    "MailService",
    "MailMessagePayloadSerializer",
    "SystemMailSenderPolicy",
    "TenantMailContextResolver",
    "TenantMailRecipientResolver",
    "TenantMailReplyPolicy",
    "TemplateMailService",
    "TemplateMailRequestPayloadSerializer",
]
