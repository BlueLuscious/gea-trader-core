from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register


@register("product_card")
class ProductCardController(Component):
    """ Render one storefront-oriented product card. """

    template_file = "product-card.html"
    css_file = "product-card.css"
    js_file = "product-card.js"

    class Kwargs(NamedTuple):
        id: str = ""
        class_name: str = ""
        product_id: str = ""
        href: str = ""
        badge_text: str = ""
        image_url: str = ""
        image_alt: str = ""
        brand_name: str = ""
        price_value: str = ""
        price_text: str = ""
        title: str = ""
        description: str = ""
        availability_text: str = "Available"
        action_label: str = "Add"

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict[str, str]:
        """ Normalize the public product-card data.

        Args:
            args: Positional component args.
            kwargs: Typed keyword arguments passed into the component.
            slots: Component slot registry.
            context: Parent render context.

        Returns:
            dict[str, str]: Normalized template data for the product card.
        """
        component_id = kwargs.id or f"gc-product-card-{uuid4().hex[:8]}"
        visual_id = f"{component_id}__visual"
        action_id = f"{component_id}__action"

        return {
            "id": component_id,
            "visual_id": visual_id,
            "action_id": action_id,
            "class_name": kwargs.class_name,
            "product_id": kwargs.product_id,
            "href": kwargs.href,
            "badge_text": kwargs.badge_text,
            "image_url": kwargs.image_url,
            "image_alt": kwargs.image_alt or kwargs.title,
            "brand_name": kwargs.brand_name,
            "price_value": kwargs.price_value,
            "price_text": kwargs.price_text,
            "title": kwargs.title,
            "description": kwargs.description,
            "availability_text": kwargs.availability_text,
            "action_label": kwargs.action_label,
        }
