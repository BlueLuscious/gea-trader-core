""" Factory that builds outbound mail DTOs from rendered templates. """

from core.mail.dtos import MailMessageDTO, TemplateMailRequestDTO
from core.mail.renderers import MailTemplateRenderer


class TemplateMailMessageFactory:
    """ Build outbound mail DTOs from template names and context. """

    renderer_class = MailTemplateRenderer

    @classmethod
    def build(
        cls,
        *,
        request: TemplateMailRequestDTO,
        from_email: str | None = None,
    ) -> MailMessageDTO:
        """ Build one outbound mail DTO from one template pair.

        Args:
            request: Templated outbound mail request.
            from_email: Optional sender override already resolved by one policy layer.

        Returns:
            MailMessageDTO: Rendered outbound mail payload.
        """
        text_body = cls.renderer_class.render_text(request.text_template_name, request.context)
        html_body = cls.renderer_class.render_html(request.html_template_name, request.context)

        return MailMessageDTO(
            subject=request.subject,
            to=request.to,
            text_body=text_body,
            html_body=html_body,
            from_email=from_email,
            cc=request.cc,
            bcc=request.bcc,
            reply_to=request.reply_to,
            headers=request.headers,
            attachments=request.attachments,
        )
