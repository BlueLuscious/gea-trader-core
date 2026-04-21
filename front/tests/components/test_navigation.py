from django.template import Context, Template
from django.test import SimpleTestCase


class NavigationComponentTests(SimpleTestCase):
    def render_template(self, template_string: str, context: dict | None = None) -> str:
        return Template(template_string).render(Context(context or {}))

    def test_topbar_renders_three_regions(self):
        html = self.render_template(
            """
            {% component "topbar" id="sample-topbar" sticky=True shadow="sm" %}
              {% fill "start" %}<span>Logo</span>{% endfill %}
              {% fill "center" %}<span>Links</span>{% endfill %}
              {% fill "end" %}<span>Actions</span>{% endfill %}
            {% endcomponent %}
            """
        )

        self.assertIn('id="sample-topbar"', html)
        self.assertIn("gc-topbar", html)
        self.assertIn("gc-topbar__section--start", html)
        self.assertIn("gc-topbar__section--center", html)
        self.assertIn("gc-topbar__section--end", html)

    def test_collapsible_renders_trigger_and_panel(self):
        html = self.render_template(
            """
            {% component "collapsible" id="sample-collapse" size="lg" panel_width="xl" close_on_escape=True %}
              {% fill "trigger" %}<span>Abrir</span>{% endfill %}
              {% fill "content" %}<a href="#">Link</a>{% endfill %}
            {% endcomponent %}
            """
        )

        self.assertIn('data-collapsible-id="sample-collapse"', html)
        self.assertIn("gc-collapsible--lg", html)
        self.assertIn("gc-collapsible--panel-xl", html)
        self.assertIn("gc-collapsible__summary", html)
        self.assertIn("gc-collapsible__panel", html)

    def test_navbar_composes_topbar_and_collapsible(self):
        html = self.render_template(
            """
            {% component "navbar" id="sample-navbar" %}
              {% fill "brand" %}<a href="/">Brand</a>{% endfill %}
              {% fill "links" %}<a href="/">Inicio</a>{% endfill %}
              {% fill "actions" %}<span>Theme</span>{% endfill %}
            {% endcomponent %}
            """
        )

        self.assertIn('id="sample-navbar"', html)
        self.assertIn('id="sample-navbar__bar"', html)
        self.assertIn('data-collapsible-id="sample-navbar__menu"', html)
        self.assertIn("gc-navbar__links--desktop", html)

    def test_sidebar_renders_dialog_structure(self):
        html = self.render_template(
            """
            {% component "sidebar" id="sample-sidebar" width="lg" aria_label="Panel de prueba" %}
              {% fill "header" %}<h2>Header</h2>{% endfill %}
              {% fill "content" %}<p>Contenido</p>{% endfill %}
              {% fill "footer" %}<button>Cerrar</button>{% endfill %}
            {% endcomponent %}
            """
        )

        self.assertIn('data-sidebar-id="sample-sidebar"', html)
        self.assertIn("gc-sidebar--width-lg", html)
        self.assertIn('role="dialog"', html)

    def test_cart_sidebar_composes_sidebar(self):
        html = self.render_template(
            """
            {% component "cart_sidebar" id="sample-cart-sidebar" %}{% endcomponent %}
            """
        )

        self.assertIn('data-cart-sidebar-id="sample-cart-sidebar"', html)
        self.assertIn('data-sidebar-id="sample-cart-sidebar__sidebar"', html)
        self.assertIn("gc-cart-sidebar__title", html)

    def test_appbar_composes_topbar(self):
        html = self.render_template(
            """
            {% component "appbar" id="sample-appbar" %}
              {% fill "leading" %}<span>Atras</span>{% endfill %}
              {% fill "title" %}<h1>Detalle</h1>{% endfill %}
              {% fill "actions" %}<span>Editar</span>{% endfill %}
            {% endcomponent %}
            """
        )

        self.assertIn('id="sample-appbar"', html)
        self.assertIn('id="sample-appbar__bar"', html)
        self.assertIn("gc-appbar__title", html)

    def test_cart_button_renders_specialized_button(self):
        html = self.render_template(
            """
            {% component "cart_button" id="sample-cart" initial_count=3 %}{% endcomponent %}
            """
        )

        self.assertIn('data-cart-button-id="sample-cart"', html)
        self.assertIn("gc-cart-button__count", html)
        self.assertIn(">3<", html)
