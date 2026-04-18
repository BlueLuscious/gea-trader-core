""" Public service exports for the mail package. """

from core.mail.services.mail_service import MailService
from core.mail.services.template_mail_service import TemplateMailService

__all__: list[str] = [
    "MailService",
    "TemplateMailService",
]
