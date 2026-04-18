""" DTO representing one outbound mail message. """

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from core.mail.dtos.mail_attachment_dto import MailAttachmentDTO
from core.mail.dtos.mail_recipient_dto import MailRecipientDTO


@dataclass(frozen=True)
class MailMessageDTO:
    """ Represent one outbound mail payload.

    Args:
        subject: Mail subject line.
        to: Primary recipients.
        text_body: Plain-text body.
        html_body: Optional HTML body.
        from_email: Optional sender override.
        cc: Optional carbon-copy recipients.
        bcc: Optional blind carbon-copy recipients.
        reply_to: Optional reply-to addresses.
        headers: Optional custom mail headers.
        attachments: Optional outbound attachments.
    """

    subject: str
    to: Sequence[MailRecipientDTO]
    text_body: str
    html_body: str | None = None
    from_email: str | None = None
    cc: Sequence[MailRecipientDTO] = field(default_factory=tuple)
    bcc: Sequence[MailRecipientDTO] = field(default_factory=tuple)
    reply_to: Sequence[str] = field(default_factory=tuple)
    headers: Mapping[str, str] = field(default_factory=dict)
    attachments: Sequence[MailAttachmentDTO] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """ Validate and normalize the outbound message payload.

        Returns:
            None
        """
        normalized_subject = self.subject.strip()
        normalized_text_body = self.text_body.strip()
        normalized_from_email = self.from_email.strip() if self.from_email else None
        normalized_reply_to = tuple(address.strip() for address in self.reply_to if address.strip())

        if not normalized_subject:
            raise ValueError("Outbound mail requires a non-empty subject.")

        if not self.to:
            raise ValueError("Outbound mail requires at least one primary recipient.")

        if not normalized_text_body:
            raise ValueError("Outbound mail requires a non-empty text body.")

        object.__setattr__(self, "subject", normalized_subject)
        object.__setattr__(self, "text_body", normalized_text_body)
        object.__setattr__(self, "from_email", normalized_from_email or None)
        object.__setattr__(self, "to", tuple(self.to))
        object.__setattr__(self, "cc", tuple(self.cc))
        object.__setattr__(self, "bcc", tuple(self.bcc))
        object.__setattr__(self, "reply_to", normalized_reply_to)
        object.__setattr__(self, "headers", dict(self.headers))
        object.__setattr__(self, "attachments", tuple(self.attachments))
