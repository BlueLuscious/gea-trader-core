from django.template import Context, Template
from django.test import Client, SimpleTestCase


class ThemeLayoutTests(SimpleTestCase):
    def render_template(self, template_string: str, context: dict | None = None) -> str:
        return Template(template_string).render(Context(context or {}))

    def test_index_renders_theme_controller_assets(self):
        response = Client(HTTP_HOST="localhost").get("/")

        self.assertEqual(response.status_code, 200)

        html = response.content.decode()
        self.assertIn("data-theme-selected", html)
        self.assertIn("js/theme-controller.js", html)
        self.assertIn("js/cart-controller.js", html)
        self.assertIn("js/base.js", html)
        self.assertIn("site-navbar", html)
        self.assertIn("data-theme-button", html)
        self.assertIn("data-cart-button", html)
        self.assertIn("data-cart-sidebar", html)

    def test_button_renders_as_generic_control(self):
        html = self.render_template(
            """
            {% component "button" icon_left_name="sun" toggle=True pressed=True %}
              {% fill "content" %}Oscuro{% endfill %}
            {% endcomponent %}
            """
        )

        self.assertIn("gc-button", html)
        self.assertIn('data-button', html)
        self.assertIn('data-button-toggle="true"', html)
        self.assertIn('aria-pressed="true"', html)
        self.assertIn("fa-sun", html)

    def test_button_accepts_data_attributes(self):
        html = self.render_template(
            """
            {% component "button" data_attrs=data_attrs %}
              {% fill "content" %}Anterior{% endfill %}
            {% endcomponent %}
            """,
            context={"data_attrs": {"carousel-prev": "true", "tracking-id": "123"}},
        )

        self.assertIn('data-carousel-prev="true"', html)
        self.assertIn('data-tracking-id="123"', html)

    def test_switch_renders_as_generic_control(self):
        html = self.render_template(
            """
            {% component "switch"
              id="theme-switch"
              label_left="Claro"
              label_right="Oscuro"
              peer_label="Tema"
            %}{% endcomponent %}
            """
        )

        self.assertIn('id="theme-switch"', html)
        self.assertIn("gc-switch", html)
        self.assertIn('data-switch-input', html)
        self.assertIn("Tema", html)

    def test_theme_button_binds_to_theme_controller(self):
        html = self.render_template(
            """
            {% component "theme_button" intent="dark" icon_only=True %}{% endcomponent %}
            """
        )

        self.assertIn("data-theme-button", html)
        self.assertIn('data-theme-intent="dark"', html)
        self.assertIn("gc-theme-button__icon", html)

    def test_theme_switch_binds_to_theme_controller(self):
        html = self.render_template(
            """
            {% component "theme_switch" id="theme-switch" light_icon="Sun" dark_icon="Moon" %}{% endcomponent %}
            """
        )

        self.assertIn("data-theme-switch", html)
        self.assertIn("data-switch-input", html)
        self.assertIn("fa-sun", html)
        self.assertIn("fa-moon", html)
