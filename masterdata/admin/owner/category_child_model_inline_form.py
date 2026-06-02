""" Owner-facing inline form for direct child categories. """

from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from core.forms import ActionInputWidget
from masterdata.models import CategoryModel


class CategoryChildModelInlineForm(forms.ModelForm):
    """ Compact owner-facing form for direct child categories. """

    def __init__(self, *args: object, **kwargs: object) -> None:
        """ Initialize the child form and configure reusable slug suggestions.

        Args:
            *args: Positional form arguments.
            **kwargs: Keyword form arguments.
        """
        super().__init__(*args, **kwargs)
        self.configure_slug_widget()

    def configure_slug_widget(self) -> None:
        """ Configure the slug field with the reusable action input widget.

        Returns:
            None: The inline form field widget is updated in place.
        """
        slug_field = self.fields["slug"]
        existing_attrs = slug_field.widget.attrs.copy()
        self.fields["slug"].widget = ActionInputWidget(
            attrs=existing_attrs,
            action_url=reverse("owner_admin:masterdata_categorymodel_suggest_slug"),
            action_label=_("Suggest slug"),
            response_value_key="slug",
            source_params=[
                {
                    "name": "name",
                    "selector": 'input[id$="-name"]',
                    "scope": "closest",
                    "closest_selector": "tr",
                },
                {
                    "name": "parent_slug",
                    "selector": "#id_slug",
                    "scope": "document",
                },
            ],
            static_params={
                "object_id": str(self.instance.pk or ""),
            },
        )

    class Meta:
        """ Configure the inline form for child-category editing. """

        model = CategoryModel
        fields = (
            "name",
            "slug",
            "sort_order",
            "is_active",
        )
        labels = {
            "name": _("Subcategory name"),
            "slug": _("URL slug"),
            "sort_order": _("Display order"),
            "is_active": _("Available for products"),
        }
        help_texts = {
            "slug": _("Usually created from the subcategory name. Adjust it only when you need a custom URL."),
            "sort_order": _("Lower values appear first inside this parent category."),
        }
