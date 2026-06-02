""" Generic text input widget with one configurable action button. """

import json
from typing import Any
from django import forms
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.widgets import BUTTON_CLASSES, INPUT_CLASSES


class ActionInputWidget(forms.TextInput):
    """ Render a text input with an inline server-backed action button. """

    template_name = "core/forms/widgets/action_input_widget.html"

    class Media:
        """ Load generic assets for action input widgets. """

        css = {
            "all": ("core/forms/widgets/action_input_widget.css",),
        }
        js = ("core/forms/widgets/action_input_widget.js",)

    def __init__(
        self,
        attrs: dict[str, Any] | None = None,
        *,
        action_url: str = "",
        action_label: str | None = None,
        response_value_key: str = "value",
        source_params: list[dict[str, str]] | None = None,
        static_params: dict[str, str] | None = None,
    ) -> None:
        """ Initialize one action input widget.

        Args:
            attrs: Optional widget HTML attributes.
            action_url: URL called when the action button is clicked.
            action_label: Button label shown next to the input.
            response_value_key: JSON response key used to update the input value.
            source_params: Request params collected from other form controls.
            static_params: Static request params sent with every action call.
        """
        super().__init__(attrs)
        self.action_url = action_url
        self.action_label = action_label or _("Run action")
        self.response_value_key = response_value_key
        self.source_params = source_params or []
        self.static_params = static_params or {}

    def get_context(self, name: str, value: Any, attrs: dict[str, Any] | None) -> dict[str, Any]:
        """ Build template context for the action input.

        Args:
            name: Bound field name.
            value: Current field value.
            attrs: Optional HTML attributes for the rendered input.

        Returns:
            dict[str, Any]: Widget context enriched with action configuration.
        """
        context = super().get_context(name, value, attrs)
        context["widget"]["attrs"] = self._build_input_attrs(context["widget"]["attrs"])
        context["widget"]["attrs_html"] = mark_safe(flatatt(context["widget"]["attrs"]))
        context["widget"]["action_url"] = self.action_url
        context["widget"]["action_label"] = self.action_label
        context["widget"]["button_classes"] = self.get_button_classes()
        context["widget"]["response_value_key"] = self.response_value_key
        context["widget"]["source_params_json"] = self._json_data(self.source_params)
        context["widget"]["static_params_json"] = self._json_data(self.static_params)
        return context

    def get_button_classes(self) -> str:
        """ Return Unfold-compatible classes for the inline action button.

        Returns:
            str: CSS classes aligned with Unfold admin buttons.
        """
        classes = [
            *BUTTON_CLASSES,
            "core-action-input__button",
            "gap-2",
            "group",
            "hover:bg-primary-600/80",
            "inline-flex",
            "items-center",
            "justify-center",
            "relative",
            "transition-all",
        ]
        return " ".join(classes)

    def _build_input_attrs(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """ Merge Unfold-compatible classes into the input attributes.

        Args:
            attrs: Input attributes built by Django.

        Returns:
            dict[str, Any]: Input attributes with project styling classes.
        """
        input_attrs = attrs.copy()
        existing_classes = input_attrs.get("class", "")
        input_attrs["class"] = self._merge_classes(
            [
                *INPUT_CLASSES,
                "core-action-input__control",
                existing_classes,
            ]
        )
        return input_attrs

    def _merge_classes(self, class_groups: list[str]) -> str:
        """ Merge CSS class groups while keeping their first occurrence order.

        Args:
            class_groups: CSS class strings or individual class names to merge.

        Returns:
            str: Space-separated CSS class list without duplicates.
        """
        merged_classes: list[str] = []
        seen_classes: set[str] = set()
        for class_group in class_groups:
            for class_name in class_group.split():
                if class_name in seen_classes:
                    continue
                merged_classes.append(class_name)
                seen_classes.add(class_name)

        return " ".join(merged_classes)

    def _json_data(self, value: Any) -> str:
        """ Serialize widget configuration as safe JSON for data attributes.

        Args:
            value: Python value to serialize.

        Returns:
            str: JSON string safe for HTML data attributes.
        """
        return json.dumps(value)
