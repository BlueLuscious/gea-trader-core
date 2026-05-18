""" Shared form field for bounded nested JSON key-value data. """

from typing import Any
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from core.forms.widgets import NestedJsonKeyValueWidget

NestedJsonValue = str | dict[str, Any]
NestedJsonDict = dict[str, NestedJsonValue]


class NestedJsonKeyValueField(forms.Field):
    """ Normalize nested key-value rows into a bounded JSON-compatible dictionary. """

    max_allowed_depth = 4
    default_error_messages = {
        "invalid": _("Enter a valid nested key-value list."),
        "invalid_depth": _("Nested key-value depth is not valid."),
        "missing_key": _("Keys are required when a value or child rows are provided."),
        "duplicate_key": _("Keys must be unique within the same level."),
        "max_depth": _("Nested key-value rows exceed the allowed depth."),
        "mixed_node": _("A key cannot have both a value and child rows."),
    }

    def __init__(
        self,
        *args: Any,
        max_depth: int = 2,
        key_label: str | None = None,
        value_label: str | None = None,
        add_label: str | None = None,
        add_child_label: str | None = None,
        remove_label: str | None = None,
        **kwargs: Any,
    ) -> None:
        """ Initialize one bounded nested JSON key-value field.

        Args:
            *args: Positional field arguments.
            max_depth: Maximum allowed nesting depth, starting at ``1`` for root rows.
            key_label: Optional label for the key column.
            value_label: Optional label for the value column.
            add_label: Optional label for the add-root-row action.
            add_child_label: Optional label for the add-child-row action.
            remove_label: Optional label for the remove-row action.
            **kwargs: Keyword field arguments.

        Raises:
            ValueError: When ``max_depth`` is outside the supported bounds.
        """
        self.validate_max_depth(max_depth)
        self.max_depth = max_depth
        kwargs.setdefault(
            "widget",
            NestedJsonKeyValueWidget(
                max_depth=max_depth,
                key_label=key_label,
                value_label=value_label,
                add_label=add_label,
                add_child_label=add_child_label,
                remove_label=remove_label,
            ),
        )
        super().__init__(*args, **kwargs)

    def validate_max_depth(self, max_depth: int) -> None:
        """ Validate the configured maximum nesting depth.

        Args:
            max_depth: Maximum allowed nesting depth.

        Raises:
            ValueError: When the provided depth is outside supported bounds.
        """
        if max_depth < 1 or max_depth > self.max_allowed_depth:
            raise ValueError(
                f"max_depth must be between 1 and {self.max_allowed_depth}."
            )

    def to_python(self, value: Any) -> NestedJsonDict:
        """ Convert nested submitted rows or dictionaries into a normalized dictionary.

        Args:
            value: Submitted rows or current dictionary value.

        Returns:
            NestedJsonDict: Normalized nested dictionary.

        Raises:
            ValidationError: When the submitted value cannot be normalized.
        """
        if value in self.empty_values:
            return {}

        if isinstance(value, dict):
            return self.clean_mapping(value, depth=1)

        if isinstance(value, list | tuple):
            return self.clean_rows(value)

        raise ValidationError(self.error_messages["invalid"], code="invalid")

    def clean_mapping(self, value: dict[Any, Any], *, depth: int) -> NestedJsonDict:
        """ Normalize an existing nested dictionary value.

        Args:
            value: Existing dictionary value.
            depth: Current nesting depth.

        Returns:
            NestedJsonDict: Normalized nested dictionary.

        Raises:
            ValidationError: When the mapping exceeds depth or contains invalid values.
        """
        self.validate_depth(depth)
        normalized: NestedJsonDict = {}

        for raw_key, raw_value in value.items():
            key = str(raw_key).strip()

            if isinstance(raw_value, dict):
                child_value = self.clean_mapping(raw_value, depth=depth + 1)
                if not key and child_value:
                    raise ValidationError(self.error_messages["missing_key"], code="missing_key")
                if key and child_value:
                    normalized[key] = child_value
                continue

            if isinstance(raw_value, list | tuple):
                raise ValidationError(self.error_messages["invalid"], code="invalid")

            normalized_value = str(raw_value).strip()
            if not key and not normalized_value:
                continue

            if not key:
                raise ValidationError(self.error_messages["missing_key"], code="missing_key")

            normalized[key] = normalized_value

        return normalized

    def clean_rows(self, rows: list[Any] | tuple[Any, ...]) -> NestedJsonDict:
        """ Normalize submitted row dictionaries into a nested dictionary.

        Args:
            rows: Submitted rows with row IDs, parent IDs, keys, and values.

        Returns:
            NestedJsonDict: Normalized nested dictionary.

        Raises:
            ValidationError: When submitted rows are malformed.
        """
        parsed_rows = [
            self.parse_row(row, index=index)
            for index, row in enumerate(rows)
        ]
        children_by_parent = self.build_children_by_parent(parsed_rows)
        root_ids = children_by_parent.get("", [])
        return self.build_mapping(
            root_ids=root_ids,
            rows_by_id={row["row_id"]: row for row in parsed_rows},
            children_by_parent=children_by_parent,
            depth=1,
        )

    def parse_row(self, row: Any, *, index: int) -> dict[str, str]:
        """ Return one submitted row as a normalized row dictionary.

        Args:
            row: Submitted row dictionary or tuple.
            index: Row position used as a fallback row ID.

        Returns:
            dict[str, str]: Row data with ``row_id``, ``parent_id``, ``key``, and ``value``.

        Raises:
            ValidationError: When the row cannot be parsed.
        """
        if isinstance(row, dict):
            row_id = row.get("row_id", "")
            parent_id = row.get("parent_id", "")
            key = row.get("key", "")
            value = row.get("value", "")
        elif isinstance(row, tuple | list) and len(row) >= 4:
            row_id, parent_id, key, value = row[:4]
        else:
            raise ValidationError(self.error_messages["invalid"], code="invalid")

        normalized_row_id = str(row_id).strip() or f"__row_{index}"
        return {
            "row_id": normalized_row_id,
            "parent_id": str(parent_id).strip(),
            "key": str(key).strip(),
            "value": str(value).strip(),
        }

    def build_children_by_parent(self, rows: list[dict[str, str]]) -> dict[str, list[str]]:
        """ Group submitted row IDs by parent row ID.

        Args:
            rows: Parsed submitted row dictionaries.

        Returns:
            dict[str, list[str]]: Child row IDs grouped by parent ID.
        """
        children_by_parent: dict[str, list[str]] = {}
        row_ids = {row["row_id"] for row in rows}

        for row in rows:
            parent_id = row["parent_id"]
            if parent_id and parent_id not in row_ids:
                parent_id = ""
            children_by_parent.setdefault(parent_id, []).append(row["row_id"])

        return children_by_parent

    def build_mapping(
        self,
        *,
        root_ids: list[str],
        rows_by_id: dict[str, dict[str, str]],
        children_by_parent: dict[str, list[str]],
        depth: int,
    ) -> NestedJsonDict:
        """ Build a nested dictionary for one sibling level.

        Args:
            root_ids: Row IDs that belong to the current sibling level.
            rows_by_id: Parsed rows keyed by row ID.
            children_by_parent: Child row IDs grouped by parent row ID.
            depth: Current nesting depth.

        Returns:
            NestedJsonDict: Normalized dictionary for the current sibling level.

        Raises:
            ValidationError: When rows exceed depth or violate key rules.
        """
        self.validate_depth(depth)
        values: NestedJsonDict = {}
        seen_keys: set[str] = set()

        for row_id in root_ids:
            row = rows_by_id[row_id]
            child_ids = children_by_parent.get(row_id, [])
            has_children = self.has_meaningful_rows(child_ids, rows_by_id, children_by_parent)
            key = row["key"]
            value = row["value"]

            if not key and not value and not has_children:
                continue

            if not key:
                raise ValidationError(self.error_messages["missing_key"], code="missing_key")

            if key in seen_keys:
                raise ValidationError(self.error_messages["duplicate_key"], code="duplicate_key")

            if value and has_children:
                raise ValidationError(self.error_messages["mixed_node"], code="mixed_node")

            seen_keys.add(key)
            if has_children:
                values[key] = self.build_mapping(
                    root_ids=child_ids,
                    rows_by_id=rows_by_id,
                    children_by_parent=children_by_parent,
                    depth=depth + 1,
                )
                continue

            values[key] = value

        return values

    def has_meaningful_rows(
        self,
        row_ids: list[str],
        rows_by_id: dict[str, dict[str, str]],
        children_by_parent: dict[str, list[str]],
    ) -> bool:
        """ Return whether any row in a subtree contains data.

        Args:
            row_ids: Row IDs to inspect.
            rows_by_id: Parsed rows keyed by row ID.
            children_by_parent: Child row IDs grouped by parent row ID.

        Returns:
            bool: ``True`` when any row in the subtree has key, value, or descendants.
        """
        for row_id in row_ids:
            row = rows_by_id[row_id]
            child_ids = children_by_parent.get(row_id, [])
            if row["key"] or row["value"] or self.has_meaningful_rows(
                child_ids,
                rows_by_id,
                children_by_parent,
            ):
                return True

        return False

    def validate_depth(self, depth: int) -> None:
        """ Validate the current normalization depth.

        Args:
            depth: Current nesting depth.

        Raises:
            ValidationError: When the current depth exceeds ``max_depth``.
        """
        if depth > self.max_depth:
            raise ValidationError(self.error_messages["max_depth"], code="max_depth")
