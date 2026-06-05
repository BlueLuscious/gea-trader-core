""" Tests for the reusable action input widget. """

from django import forms
from django.utils.translation import override
from core.forms import ActionInputWidget
from core.forms.widgets import UNFOLD_READONLY_VALUE_CLASSES
from core.testing.base import LoggedSimpleTestCase


class TestActionInputWidget(LoggedSimpleTestCase):
    """ Verify action input widgets render reusable server-backed controls. """

    def test_context_exposes_action_configuration(self) -> None:
        """ Verify widget context carries action settings and source params. """
        widget = ActionInputWidget(
            action_url="/admin/example/suggest/",
            action_label="Suggest",
            response_value_key="slug",
            source_params=[
                {
                    "name": "name",
                    "selector": "#id_name",
                    "scope": "document",
                }
            ],
            static_params={"object_id": "7"},
        )

        context = widget.get_context("slug", "current-slug", {"id": "id_slug"})

        self.assertEqual("/admin/example/suggest/", context["widget"]["action_url"])
        self.assertEqual("Suggest", context["widget"]["action_label"])
        self.assertEqual("slug", context["widget"]["response_value_key"])
        self.assertIn('"name": "name"', context["widget"]["source_params_json"])
        self.assertIn('"object_id": "7"', context["widget"]["static_params_json"])
        self.assertIn("core-action-input__control", context["widget"]["attrs"]["class"])
        self.assertIn("border-base-200", context["widget"]["attrs"]["class"])
        self.assertIn("core-action-input__button", context["widget"]["button_classes"])
        self.assertIn("bg-primary-600", context["widget"]["button_classes"])
        self.assertIn("hover:bg-primary-600/80", context["widget"]["button_classes"])
        self.assertIn("inline-flex", context["widget"]["button_classes"])

    def test_render_outputs_input_button_and_data_contract(self) -> None:
        """ Verify rendered HTML exposes the generic JavaScript contract. """
        class ExampleForm(forms.Form):
            """ Small form used to render the action input widget. """

            slug = forms.CharField(
                widget=ActionInputWidget(
                    action_url="/admin/example/suggest/",
                    action_label="Suggest",
                    response_value_key="slug",
                    source_params=[
                        {
                            "name": "name",
                            "selector": "#id_name",
                            "scope": "document",
                        }
                    ],
                )
            )

        rendered_form = ExampleForm(initial={"slug": "current-slug"}).as_p()

        self.assertIn('data-action-input-widget', rendered_form)
        self.assertIn('data-action-input-url="/admin/example/suggest/"', rendered_form)
        self.assertIn('data-action-input-response-key="slug"', rendered_form)
        self.assertIn('data-action-input-control', rendered_form)
        self.assertIn('data-action-input-button', rendered_form)
        self.assertIn('class="border cursor-pointer font-medium', rendered_form)
        self.assertIn('value="current-slug"', rendered_form)
        self.assertIn("Suggest", rendered_form)

    def test_readonly_render_outputs_display_without_action_controls(self) -> None:
        """ Verify locked action inputs render display text without interactive controls. """
        widget = ActionInputWidget(
            action_url="/admin/example/suggest/",
            action_label="Suggest",
            response_value_key="slug",
        )

        rendered = widget.render("slug", "current-slug", attrs={"readonly": True})

        for class_name in ("readonly", "bg-base-50", "dark:bg-base-800", "rounded-default", "shadow-xs"):
            self.assertIn(class_name, UNFOLD_READONLY_VALUE_CLASSES)
            self.assertIn(class_name, rendered)

        self.assertIn("core-action-input__display", rendered)
        self.assertIn("readonly", rendered)
        self.assertIn("current-slug", rendered)
        self.assertNotIn("data-action-input-widget", rendered)
        self.assertNotIn("data-action-input-url", rendered)
        self.assertNotIn("data-action-input-control", rendered)
        self.assertNotIn("data-action-input-button", rendered)

    def test_readonly_empty_render_outputs_dash_placeholder(self) -> None:
        """ Verify locked empty action inputs render a dash placeholder. """
        widget = ActionInputWidget(
            action_url="/admin/example/suggest/",
            action_label="Suggest",
        )

        rendered = widget.render("slug", "", attrs={"disabled": True})

        self.assertIn("core-action-input__display", rendered)
        self.assertIn("-", rendered)
        self.assertNotIn("data-action-input-control", rendered)
        self.assertNotIn("data-action-input-button", rendered)

    def test_media_includes_generic_assets(self) -> None:
        """ Verify the widget loads its reusable CSS and JavaScript assets. """
        rendered_media = str(ActionInputWidget().media)

        self.assertIn("core/forms/widgets/action_input_widget.css", rendered_media)
        self.assertIn("core/forms/widgets/action_input_widget.js", rendered_media)

    def test_default_action_label_is_translatable(self) -> None:
        """ Verify the fallback button label uses the translation workflow. """
        with override("es"):
            context = ActionInputWidget().get_context("slug", "", {})

        self.assertEqual("Ejecutar acción", str(context["widget"]["action_label"]))
