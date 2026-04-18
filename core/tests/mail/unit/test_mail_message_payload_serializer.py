""" Tests for the raw mail payload serializer. """

from core.mail import (
    MailAttachmentDTO,
    MailMessageDTO,
    MailMessagePayloadSerializer,
    MailRecipientDTO,
)
from core.testing import LoggedSimpleTestCase


class TestMailMessagePayloadSerializer(LoggedSimpleTestCase):
    """ Verify raw mail payloads can be serialized for Celery transport. """

    def test_roundtrip_preserves_recipients_bodies_and_attachments(self) -> None:
        """ Serialize and deserialize one raw mail message without losing payload data. """
        message = MailMessageDTO(
            subject="Serializer test",
            to=[MailRecipientDTO(email="owner@example.com", name="Owner User")],
            text_body="Plain body",
            html_body="<p>Plain body</p>",
            from_email="noreply@example.com",
            cc=[MailRecipientDTO(email="cc@example.com")],
            bcc=[MailRecipientDTO(email="bcc@example.com")],
            reply_to=["reply@example.com"],
            headers={"X-Test": "serializer"},
            attachments=[MailAttachmentDTO(filename="report.txt", content="ok", mimetype="text/plain")],
        )

        payload = MailMessagePayloadSerializer.serialize(message)
        rebuilt_message = MailMessagePayloadSerializer.deserialize(payload)

        self.assertEqual(message.subject, rebuilt_message.subject)
        self.assertEqual(message.to[0].email, rebuilt_message.to[0].email)
        self.assertEqual(message.html_body, rebuilt_message.html_body)
        self.assertEqual(message.reply_to, rebuilt_message.reply_to)
        self.assertEqual(message.attachments[0].filename, rebuilt_message.attachments[0].filename)
