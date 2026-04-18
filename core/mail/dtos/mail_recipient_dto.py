""" DTO representing one outbound mail recipient. """

from dataclasses import dataclass
from email.utils import formataddr


@dataclass(frozen=True)
class MailRecipientDTO:
    """ Represent one mail recipient with an optional display name.

    Args:
        email: Recipient email address.
        name: Optional human-readable display name.
    """

    email: str
    name: str | None = None

    def __post_init__(self) -> None:
        """ Validate and normalize the recipient fields.

        Returns:
            None
        """
        normalized_email = self.email.strip()
        normalized_name = self.name.strip() if self.name else None

        if not normalized_email:
            raise ValueError("Mail recipients require a non-empty email address.")

        object.__setattr__(self, "email", normalized_email)
        object.__setattr__(self, "name", normalized_name or None)

    def as_rfc822_address(self) -> str:
        """ Return the recipient formatted for email headers.

        Returns:
            str: RFC 822 formatted email address.
        """
        if self.name:
            return formataddr((self.name, self.email))

        return self.email
