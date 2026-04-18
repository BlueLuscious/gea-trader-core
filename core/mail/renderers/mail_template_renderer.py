""" Template rendering helpers for outbound mail. """

from collections.abc import Mapping
from typing import Any
from django.template.loader import render_to_string
from core.mail.resolvers import MailTemplateBaseContextBuilder


class MailTemplateRenderer:
    """ Render outbound mail templates into plain text or HTML strings. """

    base_context_builder_class = MailTemplateBaseContextBuilder

    @classmethod
    def render_html(cls, template_name: str, context: Mapping[str, Any]) -> str:
        """ Render one HTML mail template.

        Args:
            template_name: Django template path.
            context: Template context values.

        Returns:
            str: Rendered HTML output.
        """
        return render_to_string(template_name, cls._build_base_context(context))

    @classmethod
    def render_text(cls, template_name: str, context: Mapping[str, Any]) -> str:
        """ Render one plain-text mail template.

        Args:
            template_name: Django template path.
            context: Template context values.

        Returns:
            str: Rendered plain-text output.
        """
        return render_to_string(template_name, cls._build_base_context(context))

    @classmethod
    def _build_base_context(cls, context: Mapping[str, Any]) -> dict[str, Any]:
        """ Merge one caller context with the project mail base context.

        Args:
            context: Caller-supplied template context.

        Returns:
            dict[str, Any]: Final mail template context.
        """
        return cls.base_context_builder_class.build(context=context)
