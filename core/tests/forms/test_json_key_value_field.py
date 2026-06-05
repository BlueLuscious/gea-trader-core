""" Tests for the shared JSON key-value form field. """

from django.core.exceptions import ValidationError
from django.http import QueryDict
from django.utils.translation import override
from core.forms import JsonKeyValueField
from core.forms.widgets import UNFOLD_READONLY_VALUE_CLASSES
from core.testing.base import LoggedSimpleTestCase


class TestJsonKeyValueField(LoggedSimpleTestCase):
    """ Verify key-value rows normalize into flat dictionaries. """

    def test_returns_empty_dict_for_empty_rows(self) -> None:
        """ Verify empty submitted rows are normalized as an empty dictionary. """
        field = JsonKeyValueField(required=False)

        self.assertEqual(field.clean([("", ""), ("  ", "  ")]), {})

    def test_trims_keys_and_values(self) -> None:
        """ Verify submitted keys and values are stripped before persistence. """
        field = JsonKeyValueField(required=False)

        self.assertEqual(field.clean([(" capacidad ", " 20L ")]), {"capacidad": "20L"})

    def test_rejects_value_only_rows(self) -> None:
        """ Verify values cannot be submitted without a key. """
        field = JsonKeyValueField(required=False)

        with override("en"):
            with self.assertRaisesMessage(
                ValidationError,
                "Keys are required when a value is provided.",
            ):
                field.clean([("", "20L")])

    def test_rejects_duplicate_keys_after_trimming(self) -> None:
        """ Verify repeated keys are rejected after normalization. """
        field = JsonKeyValueField(required=False)

        with override("en"):
            with self.assertRaisesMessage(ValidationError, "Keys must be unique."):
                field.clean([("capacidad", "20L"), (" capacidad ", "205L")])

    def test_widget_reads_repeated_key_value_inputs(self) -> None:
        """ Verify the widget extracts repeated key-value row inputs from submitted data. """
        field = JsonKeyValueField(required=False)
        data = QueryDict(mutable=True)
        data.setlist("variant-attributes_json__key", ["capacidad", "presentacion"])
        data.setlist("variant-attributes_json__value", ["20L", "Tambor"])

        value = field.widget.value_from_datadict(data, {}, "variant-attributes_json")

        self.assertEqual(value, [("capacidad", "20L"), ("presentacion", "Tambor")])

    def test_widget_returns_empty_row_when_present_without_rows(self) -> None:
        """ Verify a submitted empty widget clears the previous JSON value. """
        field = JsonKeyValueField(required=False)
        data = QueryDict(mutable=True)
        data.setlist("variant-attributes_json__present", ["1"])

        value = field.widget.value_from_datadict(data, {}, "variant-attributes_json")

        self.assertEqual(value, [("", "")])
        self.assertEqual(field.clean(value), {})

    def test_widget_present_marker_prevents_empty_value_omission(self) -> None:
        """ Verify submitted empty widgets are not treated as omitted fields. """
        field = JsonKeyValueField(required=False)
        data = QueryDict(mutable=True)
        data.setlist("variant-attributes_json__present", ["1"])

        omitted = field.widget.value_omitted_from_data(data, {}, "variant-attributes_json")

        self.assertFalse(omitted)

    def test_widget_context_uses_unfold_compatible_classes(self) -> None:
        """ Verify rendered controls receive Unfold-compatible form classes and media. """
        field = JsonKeyValueField(required=False)
        context = field.widget.get_context("variant-attributes_json", {}, {})
        rendered_media = str(field.widget.media)

        self.assertIn("border-base-200", context["widget"]["input_classes"])
        self.assertIn("rounded-default", context["widget"]["add_button_classes"])
        self.assertIn("text-red-600", context["widget"]["remove_button_classes"])
        self.assertIn("core/forms/widgets/json_key_value_base.css", rendered_media)
        self.assertIn("core/forms/widgets/json_key_value_widget.css", rendered_media)
        self.assertIn("core/forms/widgets/json_key_value_widget.js", rendered_media)

    def test_widget_builds_rows_from_bound_submitted_values(self) -> None:
        """ Verify invalid bound forms can re-render submitted flat rows. """
        field = JsonKeyValueField(required=False)

        context = field.widget.get_context(
            "variant-attributes_json",
            [("capacidad", "20L"), ("", "Tambor")],
            {},
        )

        self.assertEqual(
            context["widget"]["rows"],
            [
                {"key": "capacidad", "value": "20L"},
                {"key": "", "value": "Tambor"},
            ],
        )

    def test_editable_widget_renders_without_disabled_attribute(self) -> None:
        """ Verify editable widgets do not require disabled or readonly attrs. """
        field = JsonKeyValueField(required=False)

        rendered = field.widget.render("variant-attributes_json", {"capacity": "20L"}, attrs={"id": "attributes"})

        self.assertIn("core-json-key-value", rendered)
        self.assertIn("capacity", rendered)
        self.assertIn("20L", rendered)
        self.assertIn("data-json-key-value-add", rendered)
        self.assertIn("data-json-key-value-remove", rendered)
        self.assertNotIn("core-json-key-value--readonly", rendered)
        self.assertNotIn("readonly disabled", rendered)

    def test_disabled_widget_renders_display_blocks_without_actions(self) -> None:
        """ Verify disabled key-value fields keep layout with display blocks only. """
        field = JsonKeyValueField(required=False, disabled=True)

        rendered = field.widget.render("variant-attributes_json", {"capacity": "20L"}, attrs={"disabled": True})

        for class_name in ("readonly", "bg-base-50", "dark:bg-base-800", "rounded-default", "shadow-xs"):
            self.assertIn(class_name, UNFOLD_READONLY_VALUE_CLASSES)
            self.assertIn(class_name, rendered)

        self.assertIn("core-json-key-value", rendered)
        self.assertIn("capacity", rendered)
        self.assertIn("20L", rendered)
        self.assertIn("core-json-key-value__display", rendered)
        self.assertIn("core-json-key-value--readonly", rendered)
        self.assertIn("readonly", rendered)
        self.assertNotIn("data-json-key-value-widget", rendered)
        self.assertNotIn("data-json-key-value-row", rendered)
        self.assertNotIn("data-json-key-value-add", rendered)
        self.assertNotIn("data-json-key-value-remove", rendered)
        self.assertNotIn('name="variant-attributes_json__present"', rendered)
        self.assertNotIn('name="variant-attributes_json__key"', rendered)
        self.assertNotIn('name="variant-attributes_json__value"', rendered)

    def test_disabled_empty_widget_renders_dash_placeholders(self) -> None:
        """ Verify disabled empty key-value fields render stable dash placeholders. """
        field = JsonKeyValueField(required=False, disabled=True)

        rendered = field.widget.render("variant-attributes_json", {}, attrs={"disabled": True})

        self.assertIn("core-json-key-value__display", rendered)
        self.assertIn("core-json-key-value--readonly", rendered)
        self.assertEqual(rendered.count("core-json-key-value__display"), 2)
        self.assertIn("-", rendered)
        self.assertNotIn("data-json-key-value-add", rendered)
        self.assertNotIn("data-json-key-value-remove", rendered)
