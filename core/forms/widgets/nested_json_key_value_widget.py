""" Shared widget for editing bounded nested JSON key-value data. """

from typing import Any
from django.utils.translation import gettext_lazy as _
from core.forms.widgets.base_json_key_value_widget import BaseJsonKeyValueWidget


class NestedJsonKeyValueWidget(BaseJsonKeyValueWidget):
    """ Render a bounded nested JSON object as key-value rows. """

    template_name = "core/forms/widgets/nested_json_key_value_widget.html"
    max_allowed_depth = 4

    class Media:
        """ Load shared assets for the nested key-value JSON editor. """

        css = {
            "all": ("core/forms/widgets/nested_json_key_value_widget.css",),
        }
        js = ("core/forms/widgets/nested_json_key_value_widget.js",)

    def __init__(
        self,
        attrs: dict[str, Any] | None = None,
        *,
        max_depth: int = 2,
        key_label: str | None = None,
        value_label: str | None = None,
        add_label: str | None = None,
        add_child_label: str | None = None,
        remove_label: str | None = None,
    ) -> None:
        """ Initialize one reusable nested key-value JSON widget.

        Args:
            attrs: Optional widget HTML attributes.
            max_depth: Maximum editable nesting depth.
            key_label: Optional label for the key column.
            value_label: Optional label for the value column.
            add_label: Optional label for the add-root-row action.
            add_child_label: Optional label for the add-child-row action.
            remove_label: Optional label for the remove-row action.
        """
        super().__init__(
            attrs,
            key_label=key_label,
            value_label=value_label,
            add_label=add_label,
            remove_label=remove_label,
        )
        self.validate_max_depth(max_depth)
        self.max_depth = max_depth
        self.add_child_label = add_child_label or _("Add child row")

    def validate_max_depth(self, max_depth: int) -> None:
        """ Validate the configured maximum nesting depth.

        Args:
            max_depth: Maximum editable nesting depth.

        Raises:
            ValueError: When the provided depth is outside supported bounds.
        """
        if max_depth < 1 or max_depth > self.max_allowed_depth:
            raise ValueError(
                f"max_depth must be between 1 and {self.max_allowed_depth}."
            )

    def get_context(self, name: str, value: Any, attrs: dict[str, Any] | None) -> dict[str, Any]:
        """ Build template context for the nested key-value editor.

        Args:
            name: Bound field name, including form prefixes.
            value: Current JSON value.
            attrs: Optional HTML attributes for the widget root.

        Returns:
            dict[str, Any]: Widget context enriched with row data and labels.
        """
        context = super().get_context(name, value, attrs)
        context["widget"]["rows"] = self.build_rows(value)
        context["widget"]["max_depth"] = self.max_depth
        context["widget"]["key_label"] = self.key_label
        context["widget"]["value_label"] = self.value_label
        context["widget"]["add_label"] = self.add_label
        context["widget"]["add_child_label"] = self.add_child_label
        context["widget"]["remove_label"] = self.remove_label
        context["widget"]["input_classes"] = self.get_input_classes()
        context["widget"]["add_button_classes"] = self.get_add_button_classes()
        context["widget"]["child_button_classes"] = self.get_child_button_classes()
        context["widget"]["remove_button_classes"] = self.get_remove_button_classes()
        return context

    def get_child_button_classes(self) -> str:
        """ Return Unfold-compatible classes for the add-child-row action.

        Returns:
            str: CSS classes aligned with the root add action.
        """
        return self.get_add_button_classes()

    def build_rows(self, value: Any) -> list[dict[str, Any]]:
        """ Convert one nested JSON value into flat template row dictionaries.

        Args:
            value: Current JSON value from the model or form.

        Returns:
            list[dict[str, Any]]: Flattened row dictionaries for the widget template.
        """
        if isinstance(value, list | tuple):
            return self.build_rows_from_submitted_rows(value)

        if not isinstance(value, dict) or not value:
            return [self.build_row(row_id="row_1", parent_id="", key="", value="", depth=1)]

        rows: list[dict[str, Any]] = []
        counter = [0]
        self.append_mapping_rows(
            rows=rows,
            value=value,
            parent_id="",
            depth=1,
            counter=counter,
        )
        return rows or [self.build_row(row_id="row_1", parent_id="", key="", value="", depth=1)]

    def append_mapping_rows(
        self,
        *,
        rows: list[dict[str, Any]],
        value: dict[Any, Any],
        parent_id: str,
        depth: int,
        counter: list[int],
    ) -> None:
        """ Append flattened rows for one dictionary level.

        Args:
            rows: Accumulated flattened rows.
            value: Dictionary to flatten.
            parent_id: Parent row identifier.
            depth: Current row depth.
            counter: Mutable counter used to generate stable row IDs.
        """
        for key, item_value in value.items():
            counter[0] += 1
            row_id = f"row_{counter[0]}"
            is_group = isinstance(item_value, dict)
            rows.append(
                self.build_row(
                    row_id=row_id,
                    parent_id=parent_id,
                    key=str(key),
                    value="" if is_group else str(item_value),
                    depth=depth,
                    has_children=is_group and bool(item_value),
                )
            )
            if is_group:
                self.append_mapping_rows(
                    rows=rows,
                    value=item_value,
                    parent_id=row_id,
                    depth=depth + 1,
                    counter=counter,
                )

    def build_row(
        self,
        *,
        row_id: str,
        parent_id: str,
        key: str,
        value: str,
        depth: int,
        has_children: bool = False,
    ) -> dict[str, Any]:
        """ Build one template row dictionary.

        Args:
            row_id: Stable row identifier.
            parent_id: Parent row identifier.
            key: Row key.
            value: Row scalar value.
            depth: Row nesting depth.
            has_children: Whether the row currently owns child rows.

        Returns:
            dict[str, Any]: Template row data.
        """
        return {
            "row_id": row_id,
            "parent_id": parent_id,
            "key": key,
            "value": value,
            "depth": depth,
            "can_add_child": depth < self.max_depth,
            "has_children": has_children,
        }

    def build_rows_from_submitted_rows(self, value: list[Any] | tuple[Any, ...]) -> list[dict[str, Any]]:
        """ Build template rows from submitted row dictionaries.

        Args:
            value: Submitted row dictionaries or row tuples.

        Returns:
            list[dict[str, Any]]: Template rows preserving submitted values.
        """
        parsed_rows = [
            self.parse_submitted_row(row, index=index)
            for index, row in enumerate(value)
        ]
        if not parsed_rows:
            return [self.build_row(row_id="row_1", parent_id="", key="", value="", depth=1)]

        children_by_parent = self.build_children_by_parent(parsed_rows)
        depths = self.build_depths(parsed_rows, children_by_parent)
        rows = [
            self.build_row(
                row_id=row["row_id"],
                parent_id=row["parent_id"],
                key=row["key"],
                value=row["value"],
                depth=depths.get(row["row_id"], 1),
                has_children=bool(children_by_parent.get(row["row_id"])),
            )
            for row in parsed_rows
        ]
        return rows or [self.build_row(row_id="row_1", parent_id="", key="", value="", depth=1)]

    def parse_submitted_row(self, row: Any, *, index: int) -> dict[str, str]:
        """ Parse one submitted row into a widget row dictionary.

        Args:
            row: Submitted row dictionary or tuple.
            index: Row position used as fallback row ID.

        Returns:
            dict[str, str]: Parsed row data.
        """
        if isinstance(row, dict):
            row_id = row.get("row_id", "")
            parent_id = row.get("parent_id", "")
            key = row.get("key", "")
            value = row.get("value", "")
        elif isinstance(row, tuple | list) and len(row) >= 4:
            row_id, parent_id, key, value = row[:4]
        else:
            row_id, parent_id, key, value = f"__row_{index}", "", "", ""

        return {
            "row_id": str(row_id).strip() or f"__row_{index}",
            "parent_id": str(parent_id).strip(),
            "key": str(key).strip(),
            "value": str(value).strip(),
        }

    def build_children_by_parent(self, rows: list[dict[str, str]]) -> dict[str, list[str]]:
        """ Group row IDs by parent row ID.

        Args:
            rows: Parsed row dictionaries.

        Returns:
            dict[str, list[str]]: Row IDs grouped by parent ID.
        """
        row_ids = {row["row_id"] for row in rows}
        children_by_parent: dict[str, list[str]] = {}
        for row in rows:
            parent_id = row["parent_id"]
            if parent_id and parent_id not in row_ids:
                parent_id = ""
            children_by_parent.setdefault(parent_id, []).append(row["row_id"])
        return children_by_parent

    def build_depths(
        self,
        rows: list[dict[str, str]],
        children_by_parent: dict[str, list[str]],
    ) -> dict[str, int]:
        """ Build row depths from parent-child relationships.

        Args:
            rows: Parsed row dictionaries.
            children_by_parent: Row IDs grouped by parent ID.

        Returns:
            dict[str, int]: Depth by row ID.
        """
        depths: dict[str, int] = {}

        def set_depth(row_id: str, depth: int) -> None:
            """ Set depth recursively for one row and its descendants.

            Args:
                row_id: Row identifier.
                depth: Current nesting depth.
            """
            depths[row_id] = depth
            for child_id in children_by_parent.get(row_id, []):
                set_depth(child_id, depth + 1)

        for root_id in children_by_parent.get("", []):
            set_depth(root_id, 1)

        for row in rows:
            depths.setdefault(row["row_id"], 1)

        return depths

    def value_from_datadict(
        self,
        data: Any,
        files: Any,
        name: str,
    ) -> list[dict[str, str]]:
        """ Return submitted nested key-value rows from form data.

        Args:
            data: Submitted form data.
            files: Submitted files, unused by this widget.
            name: Bound field name, including form prefixes.

        Returns:
            list[dict[str, str]]: Submitted nested key-value rows.
        """
        row_ids = self.get_repeated_values(data, f"{name}__row_id")
        parent_ids = self.get_repeated_values(data, f"{name}__parent_id")
        keys = self.get_repeated_values(data, f"{name}__key")
        values = self.get_repeated_values(data, f"{name}__value")
        row_count = max(len(row_ids), len(parent_ids), len(keys), len(values))

        if row_count == 0 and self.has_submitted_widget(data, name):
            return [{"row_id": "__row_0", "parent_id": "", "key": "", "value": ""}]

        return [
            {
                "row_id": str(row_ids[index]) if index < len(row_ids) else f"__row_{index}",
                "parent_id": str(parent_ids[index]) if index < len(parent_ids) else "",
                "key": str(keys[index]) if index < len(keys) else "",
                "value": str(values[index]) if index < len(values) else "",
            }
            for index in range(row_count)
        ]

    def value_omitted_from_data(self, data: Any, files: Any, name: str) -> bool:
        """ Return whether the nested key-value widget was absent from submitted data.

        Args:
            data: Submitted form data.
            files: Submitted files, unused by this widget.
            name: Bound field name, including form prefixes.

        Returns:
            bool: ``True`` only when none of the widget-owned inputs were submitted.
        """
        return self.value_omitted_from_owned_data(
            data,
            name,
            suffixes=("row_id", "parent_id", "key", "value"),
        )
