""" DTO representing one outbound templated mail request. """

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from core.mail.dtos.mail_attachment_dto import MailAttachmentDTO
from core.mail.dtos.mail_recipient_dto import MailRecipientDTO

if TYPE_CHECKING:
    from tenancy.models import TenantModel


@dataclass(frozen=True)
class TemplateMailRequestDTO:
    """ Represent one outbound templated mail request.

    Args:
        subject: Mail subject line.
        to: Primary recipients.
        context: Template context values.
        html_template_name: HTML template path.
        text_template_name: Plain-text template path.
        tenant: Optional explicit tenant used to build one tenant-aware mail context.
        from_email: Optional sender override.
        cc: Optional carbon-copy recipients.
        bcc: Optional blind carbon-copy recipients.
        reply_to: Optional reply-to addresses.
        headers: Optional custom mail headers.
        attachments: Optional outbound attachments.
    """

    subject: str
    to: Sequence[MailRecipientDTO]
    context: Mapping[str, Any]
    html_template_name: str
    text_template_name: str
    tenant: "TenantModel | None" = None
    from_email: str | None = None
    cc: Sequence[MailRecipientDTO] = field(default_factory=tuple)
    bcc: Sequence[MailRecipientDTO] = field(default_factory=tuple)
    reply_to: Sequence[str] = field(default_factory=tuple)
    headers: Mapping[str, str] = field(default_factory=dict)
    attachments: Sequence[MailAttachmentDTO] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """ Validate and normalize the outbound templated request payload.

        Returns:
            None
        """
        normalized_subject = self.subject.strip()
        normalized_html_template_name = self.html_template_name.strip()
        normalized_text_template_name = self.text_template_name.strip()
        normalized_from_email = self.from_email.strip() if self.from_email else None
        normalized_reply_to = tuple(address.strip() for address in self.reply_to if address.strip())

        if not normalized_subject:
            raise ValueError("Templated mail requires a non-empty subject.")

        if not self.to:
            raise ValueError("Templated mail requires at least one primary recipient.")

        if not normalized_html_template_name:
            raise ValueError("Templated mail requires a non-empty HTML template name.")

        if not normalized_text_template_name:
            raise ValueError("Templated mail requires a non-empty text template name.")

        object.__setattr__(self, "subject", normalized_subject)
        object.__setattr__(self, "to", tuple(self.to))
        object.__setattr__(self, "context", dict(self.context))
        object.__setattr__(self, "html_template_name", normalized_html_template_name)
        object.__setattr__(self, "text_template_name", normalized_text_template_name)
        object.__setattr__(self, "from_email", normalized_from_email or None)
        object.__setattr__(self, "cc", tuple(self.cc))
        object.__setattr__(self, "bcc", tuple(self.bcc))
        object.__setattr__(self, "reply_to", normalized_reply_to)
        object.__setattr__(self, "headers", dict(self.headers))
        object.__setattr__(self, "attachments", tuple(self.attachments))
