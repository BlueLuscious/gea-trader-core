""" Tests for the shared JSON key-value form field. """

from django.core.exceptions import ValidationError
from django.http import QueryDict
from django.utils.translation import override
from core.forms import JsonKeyValueField
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
                "Attribute keys are required when a value is provided.",
            ):
                field.clean([("", "20L")])

    def test_rejects_duplicate_keys_after_trimming(self) -> None:
        """ Verify repeated keys are rejected after normalization. """
        field = JsonKeyValueField(required=False)

        with override("en"):
            with self.assertRaisesMessage(ValidationError, "Attribute keys must be unique."):
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
        """ Verify rendered controls receive Unfold-compatible form classes. """
        field = JsonKeyValueField(required=False)
        context = field.widget.get_context("variant-attributes_json", {}, {})

        self.assertIn("border-base-200", context["widget"]["input_classes"])
        self.assertIn("rounded-default", context["widget"]["add_button_classes"])
        self.assertIn("text-red-600", context["widget"]["remove_button_classes"])
