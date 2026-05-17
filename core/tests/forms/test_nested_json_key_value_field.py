""" Tests for the shared nested JSON key-value form field. """

from django.core.exceptions import ValidationError
from django.http import QueryDict
from django.utils.translation import override
from core.forms import NestedJsonKeyValueField, NestedJsonKeyValueWidget
from core.testing.base import LoggedSimpleTestCase


class TestNestedJsonKeyValueField(LoggedSimpleTestCase):
    """ Verify nested key-value rows normalize into bounded dictionaries. """

    def test_returns_empty_dict_for_empty_rows(self) -> None:
        """ Verify empty submitted rows are normalized as an empty dictionary. """
        field = NestedJsonKeyValueField(required=False)

        self.assertEqual(
            field.clean([
                {"row_id": "root", "parent_id": "", "key": "", "value": ""},
            ]),
            {},
        )

    def test_normalizes_flat_rows_when_depth_is_one(self) -> None:
        """ Verify max depth one behaves like a flat key-value dictionary. """
        field = NestedJsonKeyValueField(required=False, max_depth=1)

        self.assertEqual(
            field.clean([
                {"row_id": "capacity", "parent_id": "", "key": " capacity ", "value": " 20L "},
                {"row_id": "packaging", "parent_id": "", "key": "packaging", "value": "Drum"},
            ]),
            {"capacity": "20L", "packaging": "Drum"},
        )

    def test_normalizes_nested_rows_when_depth_allows_children(self) -> None:
        """ Verify child rows become nested dictionaries. """
        field = NestedJsonKeyValueField(required=False, max_depth=2)

        self.assertEqual(
            field.clean([
                {"row_id": "packaging", "parent_id": "", "key": "packaging", "value": ""},
                {"row_id": "type", "parent_id": "packaging", "key": "type", "value": "drum"},
                {"row_id": "volume", "parent_id": "packaging", "key": "volume", "value": "20L"},
            ]),
            {"packaging": {"type": "drum", "volume": "20L"}},
        )

    def test_normalizes_deeper_rows_when_max_depth_allows_them(self) -> None:
        """ Verify three-level nested dictionaries are supported when configured. """
        field = NestedJsonKeyValueField(required=False, max_depth=3)

        self.assertEqual(
            field.clean([
                {"row_id": "dimensions", "parent_id": "", "key": "dimensions", "value": ""},
                {"row_id": "inner", "parent_id": "dimensions", "key": "inner", "value": ""},
                {"row_id": "width", "parent_id": "inner", "key": "width", "value": "10cm"},
            ]),
            {"dimensions": {"inner": {"width": "10cm"}}},
        )

    def test_rejects_rows_that_exceed_max_depth(self) -> None:
        """ Verify child rows fail when they exceed the configured max depth. """
        field = NestedJsonKeyValueField(required=False, max_depth=1)

        with override("en"):
            with self.assertRaisesMessage(
                ValidationError,
                "Nested key-value rows exceed the allowed depth.",
            ):
                field.clean([
                    {"row_id": "packaging", "parent_id": "", "key": "packaging", "value": ""},
                    {"row_id": "type", "parent_id": "packaging", "key": "type", "value": "drum"},
                ])

    def test_rejects_duplicate_sibling_keys(self) -> None:
        """ Verify duplicated keys are rejected only within one sibling level. """
        field = NestedJsonKeyValueField(required=False)

        with override("en"):
            with self.assertRaisesMessage(ValidationError, "Keys must be unique within the same level."):
                field.clean([
                    {"row_id": "first", "parent_id": "", "key": "capacity", "value": "20L"},
                    {"row_id": "second", "parent_id": "", "key": " capacity ", "value": "205L"},
                ])

    def test_allows_same_key_under_different_parents(self) -> None:
        """ Verify duplicate keys are allowed when they belong to different parents. """
        field = NestedJsonKeyValueField(required=False, max_depth=2)

        self.assertEqual(
            field.clean([
                {"row_id": "package", "parent_id": "", "key": "package", "value": ""},
                {"row_id": "display", "parent_id": "", "key": "display", "value": ""},
                {"row_id": "package_type", "parent_id": "package", "key": "type", "value": "drum"},
                {"row_id": "display_type", "parent_id": "display", "key": "type", "value": "card"},
            ]),
            {"package": {"type": "drum"}, "display": {"type": "card"}},
        )

    def test_rejects_value_only_rows(self) -> None:
        """ Verify scalar values cannot be submitted without a key. """
        field = NestedJsonKeyValueField(required=False)

        with override("en"):
            with self.assertRaisesMessage(
                ValidationError,
                "Keys are required when a value or child rows are provided.",
            ):
                field.clean([
                    {"row_id": "value_only", "parent_id": "", "key": "", "value": "20L"},
                ])

    def test_rejects_group_with_children_and_missing_key(self) -> None:
        """ Verify child rows cannot belong to an unnamed group. """
        field = NestedJsonKeyValueField(required=False, max_depth=2)

        with override("en"):
            with self.assertRaisesMessage(
                ValidationError,
                "Keys are required when a value or child rows are provided.",
            ):
                field.clean([
                    {"row_id": "group", "parent_id": "", "key": "", "value": ""},
                    {"row_id": "child", "parent_id": "group", "key": "type", "value": "drum"},
                ])

    def test_rejects_scalar_rows_with_child_rows(self) -> None:
        """ Verify one key cannot be both a scalar value and a nested group. """
        field = NestedJsonKeyValueField(required=False, max_depth=2)

        with override("en"):
            with self.assertRaisesMessage(
                ValidationError,
                "A key cannot have both a value and child rows.",
            ):
                field.clean([
                    {"row_id": "packaging", "parent_id": "", "key": "packaging", "value": "drum"},
                    {"row_id": "volume", "parent_id": "packaging", "key": "volume", "value": "20L"},
                ])

    def test_normalizes_existing_nested_dictionary(self) -> None:
        """ Verify existing dictionaries are normalized recursively. """
        field = NestedJsonKeyValueField(required=False, max_depth=2)

        self.assertEqual(
            field.clean({
                " packaging ": {
                    " type ": " drum ",
                    "volume": " 20L ",
                },
                " capacity ": " 20L ",
            }),
            {"packaging": {"type": "drum", "volume": "20L"}, "capacity": "20L"},
        )

    def test_rejects_invalid_max_depth_configuration(self) -> None:
        """ Verify max depth stays within the supported bounds. """
        with self.assertRaisesMessage(ValueError, "max_depth must be between 1 and 4."):
            NestedJsonKeyValueField(max_depth=5)

    def test_uses_nested_widget_with_matching_max_depth(self) -> None:
        """ Verify the field configures the nested widget with the same max depth. """
        field = NestedJsonKeyValueField(required=False, max_depth=3)

        self.assertIsInstance(field.widget, NestedJsonKeyValueWidget)
        self.assertEqual(field.widget.max_depth, 3)

    def test_widget_builds_flat_rows_from_existing_nested_dictionary(self) -> None:
        """ Verify the widget flattens nested dictionaries with depth metadata. """
        widget = NestedJsonKeyValueWidget(max_depth=3)

        rows = widget.build_rows({
            "packaging": {
                "type": "drum",
                "volume": "20L",
            },
            "capacity": "20L",
        })

        self.assertEqual(
            [
                (row["parent_id"], row["key"], row["value"], row["depth"])
                for row in rows
            ],
            [
                ("", "packaging", "", 1),
                ("row_1", "type", "drum", 2),
                ("row_1", "volume", "20L", 2),
                ("", "capacity", "20L", 1),
            ],
        )
        self.assertTrue(rows[0]["has_children"])
        self.assertFalse(rows[1]["has_children"])

    def test_widget_builds_rows_from_bound_submitted_values(self) -> None:
        """ Verify invalid bound forms can re-render submitted nested rows. """
        widget = NestedJsonKeyValueWidget(max_depth=3)

        rows = widget.build_rows([
            {"row_id": "packaging", "parent_id": "", "key": "packaging", "value": ""},
            {"row_id": "type", "parent_id": "packaging", "key": "type", "value": "drum"},
            {"row_id": "capacity", "parent_id": "", "key": "capacity", "value": "20L"},
        ])

        self.assertEqual(
            [
                (row["row_id"], row["parent_id"], row["key"], row["value"], row["depth"])
                for row in rows
            ],
            [
                ("packaging", "", "packaging", "", 1),
                ("type", "packaging", "type", "drum", 2),
                ("capacity", "", "capacity", "20L", 1),
            ],
        )
        self.assertTrue(rows[0]["has_children"])
        self.assertFalse(rows[1]["has_children"])

    def test_widget_reads_repeated_nested_row_inputs(self) -> None:
        """ Verify the widget extracts repeated nested row inputs from submitted data. """
        field = NestedJsonKeyValueField(required=False)
        data = QueryDict(mutable=True)
        data.setlist("metadata__row_id", ["packaging", "type"])
        data.setlist("metadata__parent_id", ["", "packaging"])
        data.setlist("metadata__key", ["packaging", "type"])
        data.setlist("metadata__value", ["", "drum"])

        value = field.widget.value_from_datadict(data, {}, "metadata")

        self.assertEqual(
            value,
            [
                {"row_id": "packaging", "parent_id": "", "key": "packaging", "value": ""},
                {"row_id": "type", "parent_id": "packaging", "key": "type", "value": "drum"},
            ],
        )
        self.assertEqual(field.clean(value), {"packaging": {"type": "drum"}})

    def test_widget_returns_empty_row_when_present_without_rows(self) -> None:
        """ Verify a submitted empty nested widget clears the previous JSON value. """
        field = NestedJsonKeyValueField(required=False)
        data = QueryDict(mutable=True)
        data.setlist("metadata__present", ["1"])

        value = field.widget.value_from_datadict(data, {}, "metadata")

        self.assertEqual(value, [{"row_id": "__row_0", "parent_id": "", "key": "", "value": ""}])
        self.assertEqual(field.clean(value), {})

    def test_widget_present_marker_prevents_empty_value_omission(self) -> None:
        """ Verify submitted empty nested widgets are not treated as omitted fields. """
        field = NestedJsonKeyValueField(required=False)
        data = QueryDict(mutable=True)
        data.setlist("metadata__present", ["1"])

        omitted = field.widget.value_omitted_from_data(data, {}, "metadata")

        self.assertFalse(omitted)

    def test_widget_context_includes_unfold_classes_and_max_depth(self) -> None:
        """ Verify rendered controls receive Unfold-compatible classes and depth metadata. """
        field = NestedJsonKeyValueField(required=False, max_depth=3)
        context = field.widget.get_context("metadata", {"packaging": {"type": "drum"}}, {})

        self.assertEqual(context["widget"]["max_depth"], 3)
        self.assertIn("border-base-200", context["widget"]["input_classes"])
        self.assertIn("rounded-default", context["widget"]["add_button_classes"])
        self.assertEqual(context["widget"]["child_button_classes"], context["widget"]["add_button_classes"])
        self.assertIn("text-red-600", context["widget"]["remove_button_classes"])
