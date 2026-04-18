""" DTO representing one outbound mail attachment. """

from dataclasses import dataclass


@dataclass(frozen=True)
class MailAttachmentDTO:
    """ Represent one attachment added to one outbound mail message.

    Args:
        filename: Public attachment filename.
        content: Attachment payload as text or bytes.
        mimetype: Optional content type sent with the attachment.
    """

    filename: str
    content: str | bytes
    mimetype: str | None = None

    def __post_init__(self) -> None:
        """ Validate the attachment contract.

        Returns:
            None
        """
        if not self.filename.strip():
            raise ValueError("Mail attachments require a non-empty filename.")
