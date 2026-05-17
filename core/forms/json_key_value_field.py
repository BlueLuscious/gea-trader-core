""" Shared form field for flat JSON key-value data. """

from typing import Any
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from core.forms.json_key_value_widget import JsonKeyValueWidget


class JsonKeyValueField(forms.Field):
    """ Normalize key-value form rows into a flat JSON-compatible dictionary. """

    widget = JsonKeyValueWidget
    default_error_messages = {
        "invalid": _("Enter a valid key-value list."),
        "missing_key": _("Keys are required when a value is provided."),
        "duplicate_key": _("Keys must be unique."),
    }

    def __init__(
        self,
        *args: Any,
        key_label: str | None = None,
        value_label: str | None = None,
        add_label: str | None = None,
        remove_label: str | None = None,
        **kwargs: Any,
    ) -> None:
        """ Initialize one reusable flat JSON key-value field.

        Args:
            *args: Positional field arguments.
            key_label: Optional label for the key column.
            value_label: Optional label for the value column.
            add_label: Optional label for the add-row action.
            remove_label: Optional label for the remove-row action.
            **kwargs: Keyword field arguments.
        """
        kwargs.setdefault(
            "widget",
            JsonKeyValueWidget(
                key_label=key_label,
                value_label=value_label,
                add_label=add_label,
                remove_label=remove_label,
            ),
        )
        super().__init__(*args, **kwargs)

    def to_python(self, value: Any) -> dict[str, str]:
        """ Convert submitted key-value rows into a JSONField-compatible dict.

        Args:
            value: Submitted widget value or current model value.

        Returns:
            dict[str, str]: Normalized flat dictionary.

        Raises:
            ValidationError: When submitted rows are malformed.
        """
        if value in self.empty_values:
            return {}

        if isinstance(value, dict):
            return self.clean_rows(list(value.items()))

        if isinstance(value, list | tuple):
            return self.clean_rows(value)

        raise ValidationError(self.error_messages["invalid"], code="invalid")

    def clean_rows(self, rows: list[Any] | tuple[Any, ...]) -> dict[str, str]:
        """ Normalize submitted row pairs and validate the JSON object contract.

        Args:
            rows: Submitted key-value row pairs.

        Returns:
            dict[str, str]: Normalized dictionary.

        Raises:
            ValidationError: When keys are missing or duplicated.
        """
        values: dict[str, str] = {}
        seen_keys: set[str] = set()

        for row in rows:
            key, value = self.unpack_row(row)
            normalized_key = key.strip()
            normalized_value = value.strip()

            if not normalized_key and not normalized_value:
                continue

            if not normalized_key:
                raise ValidationError(self.error_messages["missing_key"], code="missing_key")

            if normalized_key in seen_keys:
                raise ValidationError(self.error_messages["duplicate_key"], code="duplicate_key")

            seen_keys.add(normalized_key)
            values[normalized_key] = normalized_value

        return values

    def unpack_row(self, row: Any) -> tuple[str, str]:
        """ Return one row as a string key-value pair.

        Args:
            row: Submitted row from the widget or a dictionary item.

        Returns:
            tuple[str, str]: Key and value strings.
        """
        if isinstance(row, tuple | list) and len(row) >= 2:
            return str(row[0]), str(row[1])

        return "", str(row)
