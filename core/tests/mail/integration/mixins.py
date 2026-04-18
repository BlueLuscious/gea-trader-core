""" Shared mixins for MailHog-backed mail integration tests. """

import json
import os
import time
from urllib.request import urlopen
from core.mail import MailMessageDTO, MailRecipientDTO


class MailIntegrationAssertionsMixin:
    """ Define shared MailHog-backed assertions and polling helpers for mail integration tests. """

    mailhog_messages_url = os.environ.get("MAILHOG_MESSAGES_API_URL", "http://127.0.0.1:8025/api/v2/messages")
    mailhog_wait_timeout_seconds = float(os.environ.get("MAILHOG_WAIT_TIMEOUT_SECONDS", "20"))
    mailhog_poll_interval_seconds = float(os.environ.get("MAILHOG_POLL_INTERVAL_SECONDS", "0.25"))

    @classmethod
    def fetch_mailhog_messages(cls) -> list[dict[str, object]]:
        """ Fetch the current MailHog message list through its HTTP API.

        Returns:
            list[dict[str, object]]: MailHog message payloads.
        """
        with urlopen(cls.mailhog_messages_url) as response:
            payload = json.loads(response.read().decode())

        return list(payload.get("items", []))

    @classmethod
    def build_unique_message(cls, subject: str, body: str) -> MailMessageDTO:
        """ Build one integration mail payload with a unique recipient target.

        Args:
            subject: Unique subject for the integration mail.
            body: Plain-text body.

        Returns:
            MailMessageDTO: Outbound test payload.
        """
        return MailMessageDTO(
            subject=subject,
            to=[MailRecipientDTO(email="integration@example.com", name="Integration User")],
            text_body=body,
        )

    @classmethod
    def mailhog_contains_subject(cls, subject: str) -> bool:
        """ Return whether MailHog currently stores one message with the target subject.

        Args:
            subject: Subject to find in MailHog.

        Returns:
            bool: True when one captured message matches the subject.
        """
        for item in cls.fetch_mailhog_messages():
            content = item.get("Content", {})
            headers = content.get("Headers", {}) if isinstance(content, dict) else {}
            subjects = headers.get("Subject", []) if isinstance(headers, dict) else []

            if subject in subjects:
                return True

        return False

    @classmethod
    def mailhog_subject_count(cls, subject: str) -> int:
        """ Count how many captured MailHog messages match one subject.

        Args:
            subject: Subject to count.

        Returns:
            int: Number of MailHog messages carrying the subject.
        """
        matches = 0

        for item in cls.fetch_mailhog_messages():
            content = item.get("Content", {})
            headers = content.get("Headers", {}) if isinstance(content, dict) else {}
            subjects = headers.get("Subject", []) if isinstance(headers, dict) else []

            if subject in subjects:
                matches += 1

        return matches

    @classmethod
    def mailhog_contains_text(cls, text: str) -> bool:
        """ Return whether one raw MailHog payload currently contains a target text fragment.

        Args:
            text: Text fragment expected somewhere in the captured MailHog payload.

        Returns:
            bool: True when the fragment is found in one captured message payload.
        """
        payload = json.dumps(cls.fetch_mailhog_messages())
        return text in payload

    @classmethod
    def wait_for_mailhog_subject(cls, subject: str) -> None:
        """ Wait until MailHog captures one message with the given subject.

        Args:
            subject: Subject expected in MailHog.
        """
        deadline = time.monotonic() + cls.mailhog_wait_timeout_seconds

        while time.monotonic() < deadline:
            if cls.mailhog_contains_subject(subject):
                return

            time.sleep(cls.mailhog_poll_interval_seconds)

        raise AssertionError(f"MailHog did not capture subject '{subject}' within {cls.mailhog_wait_timeout_seconds} seconds.")

    @classmethod
    def wait_for_mailhog_text(cls, text: str) -> None:
        """ Wait until MailHog captures one message containing the given text fragment.

        Args:
            text: Text fragment expected in MailHog.
        """
        deadline = time.monotonic() + cls.mailhog_wait_timeout_seconds

        while time.monotonic() < deadline:
            if cls.mailhog_contains_text(text):
                return

            time.sleep(cls.mailhog_poll_interval_seconds)

        raise AssertionError(f"MailHog did not capture text '{text}' within {cls.mailhog_wait_timeout_seconds} seconds.")
