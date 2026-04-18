""" Tests for the Django mail message factory. """

from django.core.mail import EmailMultiAlternatives
from django.test import override_settings
from core.mail import MailAttachmentDTO, MailMessageDTO, MailRecipientDTO
from core.mail.factories import EmailMultiAlternativesFactory
from core.testing import LoggedSimpleTestCase


@override_settings(DEFAULT_FROM_EMAIL="noreply@example.com")
class TestEmailMultiAlternativesFactory(LoggedSimpleTestCase):
    """ Verify outbound DTOs are converted into Django email objects correctly. """

    def test_build_creates_email_with_plain_html_and_attachment_payloads(self) -> None:
        """ Build one Django email object preserving recipients, alternatives, and attachments. """
        message = MailMessageDTO(
            subject="Welcome",
            to=[MailRecipientDTO(email="owner@example.com", name="Owner User")],
            text_body="Plain body",
            html_body="<p>HTML body</p>",
            cc=[MailRecipientDTO(email="cc@example.com")],
            bcc=[MailRecipientDTO(email="bcc@example.com")],
            reply_to=["reply@example.com"],
            headers={"X-App": "gea"},
            attachments=[
                MailAttachmentDTO(
                    filename="hello.txt",
                    content="hello world",
                    mimetype="text/plain",
                )
            ],
        )

        email_message = EmailMultiAlternativesFactory.build(message)

        self.assertIsInstance(email_message, EmailMultiAlternatives)
        self.assertEqual("Welcome", email_message.subject)
        self.assertEqual("Plain body", email_message.body)
        self.assertEqual("noreply@example.com", email_message.from_email)
        self.assertEqual(["Owner User <owner@example.com>"], email_message.to)
        self.assertEqual(["cc@example.com"], email_message.cc)
        self.assertEqual(["bcc@example.com"], email_message.bcc)
        self.assertEqual(["reply@example.com"], email_message.reply_to)
        self.assertEqual({"X-App": "gea"}, email_message.extra_headers)
        self.assertEqual([("<p>HTML body</p>", "text/html")], email_message.alternatives)
        self.assertEqual(1, len(email_message.attachments))
        self.assertEqual("hello.txt", email_message.attachments[0][0])

    def test_build_prefers_message_from_email_when_provided(self) -> None:
        """ Prefer one explicit sender over the project default sender. """
        message = MailMessageDTO(
            subject="Override sender",
            to=[MailRecipientDTO(email="owner@example.com")],
            text_body="Body",
            from_email="support@example.com",
        )

        email_message = EmailMultiAlternativesFactory.build(message)

        self.assertEqual("support@example.com", email_message.from_email)
