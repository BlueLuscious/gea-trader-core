""" Shared base-template context helpers for public storefront views. """

from django.urls import reverse
from front.views.mixins.base.base_tenant_aware_mixin import BaseTenantAwareMixin
from front.views.mixins.base.tenant_aware_branding_mixin import TenantAwareBrandingMixin


class LayoutContextMixin(TenantAwareBrandingMixin, BaseTenantAwareMixin):
    """ Build shared layout context for public storefront pages and runtime views. """

    @staticmethod
    def build_site_products_url() -> str:
        """ Build the public product-list URL.

        Returns:
            str: Public product-list URL.
        """
        return reverse("product_list")

    @staticmethod
    def build_site_categories_url() -> str:
        """ Build the public category-list URL.

        Returns:
            str: Public category-list URL.
        """
        return reverse("category_list")

    @staticmethod
    def build_site_cart_state_url() -> str:
        """ Build the public cart-state URL.

        Returns:
            str: Public cart-state URL.
        """
        return reverse("cart_state")

    @staticmethod
    def build_site_cart_add_url() -> str:
        """ Build the public cart-add URL.

        Returns:
            str: Public cart-add URL.
        """
        return reverse("cart_add_item")

    @staticmethod
    def build_site_cart_update_quantity_url() -> str:
        """ Build the public cart-update-quantity URL.

        Returns:
            str: Public cart-update-quantity URL.
        """
        return reverse("cart_update_quantity")

    @staticmethod
    def build_site_cart_remove_url() -> str:
        """ Build the public cart-remove URL.

        Returns:
            str: Public cart-remove URL.
        """
        return reverse("cart_remove_item")

    @staticmethod
    def build_site_cart_clear_url() -> str:
        """ Build the public cart-clear URL.

        Returns:
            str: Public cart-clear URL.
        """
        return reverse("cart_clear")

    @staticmethod
    def build_site_cart_quote_url() -> str:
        """ Build the public cart quote-request URL.

        Returns:
            str: Public cart quote-request URL.
        """
        return reverse("cart_quote_request")

    def build_layout_context(self) -> dict[str, object]:
        """ Build the shared layout context for the public storefront shell.

        Returns:
            dict[str, object]: Shared layout context for the base template.
        """
        tenant = self.get_tenant()
        context = self.build_tenant_branding_context(tenant)
        context.update(
            site_home_url="/",
            site_products_url=self.build_site_products_url(),
            site_categories_url=self.build_site_categories_url(),
            site_cart_state_url=self.build_site_cart_state_url(),
            site_cart_add_url=self.build_site_cart_add_url(),
            site_cart_update_quantity_url=self.build_site_cart_update_quantity_url(),
            site_cart_remove_url=self.build_site_cart_remove_url(),
            site_cart_clear_url=self.build_site_cart_clear_url(),
            site_cart_quote_url=self.build_site_cart_quote_url(),
            carrousel_prev_attrs={"carousel-prev": "true"},
            carrousel_next_attrs={"carousel-next": "true"},
        )
        return context

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """ Extend context with shared public storefront layout data.

        Args:
            **kwargs: Generic view context keyword arguments.

        Returns:
            dict[str, object]: Context extended with shared public layout data.
        """
        context = super().get_context_data(**kwargs)
        self.ensure_session_key(self.request)
        context.update(self.build_layout_context())
        return context
