""" Shared widget for editing flat JSON key-value data. """

from typing import Any
from core.forms.widgets.base_json_key_value_widget import BaseJsonKeyValueWidget


class JsonKeyValueWidget(BaseJsonKeyValueWidget):
    """ Render a flat JSON object as reusable key-value rows. """

    template_name = "core/forms/widgets/json_key_value_widget.html"

    class Media:
        """ Load shared assets for the key-value JSON editor. """

        css = {
            "all": ("core/forms/widgets/json_key_value_widget.css",),
        }
        js = ("core/forms/widgets/json_key_value_widget.js",)

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
        super().__init__(
            attrs,
            key_label=key_label,
            value_label=value_label,
            add_label=add_label,
            remove_label=remove_label,
        )

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

    def build_rows(self, value: Any) -> list[dict[str, str]]:
        """ Convert one JSON value into template row dictionaries.

        Args:
            value: Current JSON value from the model or submitted bound rows.

        Returns:
            list[dict[str, str]]: Key-value rows for the widget template.
        """
        if isinstance(value, list | tuple):
            rows = [
                self.build_row_from_submitted_value(row)
                for row in value
            ]
            return rows or [{"key": "", "value": ""}]

        if isinstance(value, dict):
            rows = [
                {"key": str(key), "value": str(item_value)}
                for key, item_value in value.items()
            ]
            return rows or [{"key": "", "value": ""}]

        return [{"key": "", "value": ""}]

    def build_row_from_submitted_value(self, row: Any) -> dict[str, str]:
        """ Convert one submitted row into a template row dictionary.

        Args:
            row: Submitted row tuple, list, or fallback scalar value.

        Returns:
            dict[str, str]: Row dictionary preserving submitted key and value.
        """
        if isinstance(row, tuple | list) and len(row) >= 2:
            return {"key": str(row[0]), "value": str(row[1])}

        return {"key": "", "value": str(row)}

    def value_from_datadict(self, data: Any, files: Any, name: str) -> list[tuple[str, str]]:
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
        return self.value_omitted_from_owned_data(data, name, suffixes=("key", "value"))
