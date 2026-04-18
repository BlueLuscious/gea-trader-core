""" Mail factory exports. """

from core.mail.factories.email_multi_alternatives_factory import EmailMultiAlternativesFactory
from core.mail.factories.template_mail_message_factory import TemplateMailMessageFactory

__all__: list[str] = ["EmailMultiAlternativesFactory", "TemplateMailMessageFactory"]
