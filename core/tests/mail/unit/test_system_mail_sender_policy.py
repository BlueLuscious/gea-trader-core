""" Tests for the system mail sender policy. """

from core.mail import SystemMailSenderPolicy
from core.testing import LoggedSimpleTestCase


class TestSystemMailSenderPolicy(LoggedSimpleTestCase):
    """ Verify the system mail sender policy stays conservative. """

    def test_resolve_returns_none_when_no_explicit_sender_exists(self) -> None:
        """ Return None so Django falls back to the configured system sender. """
        self.assertIsNone(SystemMailSenderPolicy.resolve())

    def test_resolve_returns_the_explicit_sender_when_provided(self) -> None:
        """ Return one explicit sender override unchanged apart from surrounding whitespace. """
        self.assertEqual(
            "sender@example.com",
            SystemMailSenderPolicy.resolve(explicit_from_email=" sender@example.com "),
        )
