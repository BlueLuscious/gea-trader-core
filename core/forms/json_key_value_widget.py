""" Shared widget for editing flat JSON key-value data. """

from typing import Any
from django import forms
from django.utils.translation import gettext_lazy as _
from unfold.widgets import INPUT_CLASSES


class JsonKeyValueWidget(forms.Widget):
    """ Render a flat JSON object as reusable key-value rows. """

    template_name = "core/forms/widgets/json_key_value_widget.html"

    class Media:
        """ Load shared assets for the key-value JSON editor. """

        css = {
            "all": ("core/forms/json_key_value_widget.css",),
        }
        js = ("core/forms/json_key_value_widget.js",)

    def __init__(
        self,
        attrs: dict[str, Any] | None = None,
        *,
        key_label: str | None = None,
        value_label: str | None = None,
        add_label: str | None = None,
        remove_label: str | None = None,
    ) -> None:
        """ Initialize one reusable key-value JSON widget.

        Args:
            attrs: Optional widget HTML attributes.
            key_label: Optional label for the key column.
            value_label: Optional label for the value column.
            add_label: Optional label for the add-row action.
            remove_label: Optional label for the remove-row action.
        """
        super().__init__(attrs)
        self.key_label = key_label or _("Attribute key")
        self.value_label = value_label or _("Attribute value")
        self.add_label = add_label or _("Add attribute")
        self.remove_label = remove_label or _("Remove attribute")

    def get_context(self, name: str, value: Any, attrs: dict[str, Any] | None) -> dict[str, Any]:
        """ Build template context for the key-value editor.

        Args:
            name: Bound field name, including form prefixes.
            value: Current JSON value.
            attrs: Optional HTML attributes for the widget root.

        Returns:
            dict[str, Any]: Widget context enriched with row data and labels.
        """
        context = super().get_context(name, value, attrs)
        context["widget"]["rows"] = self.build_rows(value)
        context["widget"]["key_label"] = self.key_label
        context["widget"]["value_label"] = self.value_label
        context["widget"]["add_label"] = self.add_label
        context["widget"]["remove_label"] = self.remove_label
        context["widget"]["input_classes"] = self.get_input_classes()
        context["widget"]["add_button_classes"] = self.get_add_button_classes()
        context["widget"]["remove_button_classes"] = self.get_remove_button_classes()
        return context

    def get_input_classes(self) -> str:
        """ Return Unfold-compatible text input classes for widget rows.

        Returns:
            str: CSS classes aligned with Unfold text inputs.
        """
        return " ".join(INPUT_CLASSES)

    def get_add_button_classes(self) -> str:
        """ Return Unfold-compatible classes for the add-row action.

        Returns:
            str: CSS classes aligned with a secondary admin action.
        """
        classes = [
            "border",
            "border-base-200",
            "cursor-pointer",
            "font-medium",
            "px-3",
            "py-2",
            "rounded-default",
            "shadow-xs",
            "text-font-important-light",
            "text-sm",
            "transition-all",
            "whitespace-nowrap",
            "hover:bg-base-50",
            "dark:border-base-700",
            "dark:text-font-important-dark",
            "dark:hover:bg-base-900",
        ]
        return " ".join(classes)

    def get_remove_button_classes(self) -> str:
        """ Return Unfold-compatible classes for the remove-row action.

        Returns:
            str: CSS classes aligned with a compact destructive admin action.
        """
        classes = [
            "border",
            "border-base-200",
            "cursor-pointer",
            "flex",
            "font-medium",
            "h-[38px]",
            "items-center",
            "justify-center",
            "px-0",
            "py-0",
            "rounded-default",
            "shadow-xs",
            "text-center",
            "text-red-600",
            "text-sm",
            "transition-all",
            "w-[38px]",
            "hover:bg-red-50",
            "dark:border-base-700",
            "dark:text-red-500",
            "dark:hover:bg-red-500/20",
        ]
        return " ".join(classes)

    def build_rows(self, value: Any) -> list[dict[str, str]]:
        """ Convert one JSON value into template row dictionaries.

        Args:
            value: Current JSON value from the model or form.

        Returns:
            list[dict[str, str]]: Key-value rows for the widget template.
        """
        if isinstance(value, dict):
            rows = [
                {"key": str(key), "value": str(item_value)}
                for key, item_value in value.items()
            ]
            return rows or [{"key": "", "value": ""}]

        return [{"key": "", "value": ""}]

    def value_from_datadict(
        self,
        data: Any,
        files: Any,
        name: str,
    ) -> list[tuple[str, str]]:
        """ Return submitted key-value rows from form data.

        Args:
            data: Submitted form data.
            files: Submitted files, unused by this widget.
            name: Bound field name, including form prefixes.

        Returns:
            list[tuple[str, str]]: Submitted key-value pairs.
        """
        keys = self.get_repeated_values(data, f"{name}__key")
        values = self.get_repeated_values(data, f"{name}__value")
        row_count = max(len(keys), len(values))

        if row_count == 0 and self.has_submitted_widget(data, name):
            return [("", "")]

        return [
            (
                str(keys[index]) if index < len(keys) else "",
                str(values[index]) if index < len(values) else "",
            )
            for index in range(row_count)
        ]

    def has_submitted_widget(self, data: Any, name: str) -> bool:
        """ Return whether the widget was present in submitted form data.

        Args:
            data: Submitted form data.
            name: Bound field name, including form prefixes.

        Returns:
            bool: ``True`` when the widget's presence marker was submitted.
        """
        present_key = f"{name}__present"
        if hasattr(data, "getlist"):
            return bool(data.getlist(present_key))

        return present_key in data

    def value_omitted_from_data(self, data: Any, files: Any, name: str) -> bool:
        """ Return whether the key-value widget was absent from submitted data.

        Django uses this hook to decide whether an empty value should preserve a
        model field default. The key-value widget posts suffixed input names, so
        the default widget implementation would incorrectly treat an intentionally
        empty editor as omitted.

        Args:
            data: Submitted form data.
            files: Submitted files, unused by this widget.
            name: Bound field name, including form prefixes.

        Returns:
            bool: ``True`` only when none of the widget-owned inputs were submitted.
        """
        return not (
            self.has_submitted_widget(data, name)
            or self.get_repeated_values(data, f"{name}__key")
            or self.get_repeated_values(data, f"{name}__value")
        )

    def get_repeated_values(self, data: Any, key: str) -> list[Any]:
        """ Return submitted values from QueryDict-like or plain dictionary data.

        Args:
            data: Submitted form data.
            key: Submitted input name.

        Returns:
            list[Any]: Values submitted for the provided key.
        """
        if hasattr(data, "getlist"):
            return list(data.getlist(key))

        value = data.get(key, "")
        if isinstance(value, list | tuple):
            return list(value)

        return [value] if value != "" else []
