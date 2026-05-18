""" Tests for the templated mail request DTO. """

from core.mail import MailRecipientDTO, TemplateMailRequestDTO
from core.testing import LoggedSimpleTestCase


class TestTemplateMailRequestDTO(LoggedSimpleTestCase):
    """ Verify the templated mail request DTO validates and normalizes its payload. """

    def test_normalizes_subject_template_names_and_reply_to_values(self) -> None:
        """ Normalize the main templated mail request fields into stable immutable values. """
        request = TemplateMailRequestDTO(
            subject="  Template request  ",
            to=[MailRecipientDTO(email="owner@example.com")],
            context={"mail_title": "Template request"},
            html_template_name="  core/mail/messages/test_message.html  ",
            text_template_name="  core/mail/messages/test_message.txt  ",
            reply_to=[" reply@example.com ", ""],
        )

        self.assertEqual("Template request", request.subject)
        self.assertEqual("core/mail/messages/test_message.html", request.html_template_name)
        self.assertEqual("core/mail/messages/test_message.txt", request.text_template_name)
        self.assertEqual(("reply@example.com",), request.reply_to)
        self.assertEqual({"mail_title": "Template request"}, request.context)

    def test_raises_when_the_template_names_are_empty(self) -> None:
        """ Reject templated mail requests without explicit template paths. """
        with self.assertRaisesMessage(ValueError, "Templated mail requires a non-empty HTML template name."):
            TemplateMailRequestDTO(
                subject="Template request",
                to=[MailRecipientDTO(email="owner@example.com")],
                context={},
                html_template_name=" ",
                text_template_name="core/mail/messages/test_message.txt",
            )
