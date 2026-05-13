""" Shared base-template context helpers for public storefront views. """

from front.views.mixins.base.base_tenant_aware_mixin import BaseTenantAwareMixin
from front.views.mixins.base.layout_urls_mixin import LayoutUrlsMixin
from front.views.mixins.base.tenant_aware_branding_mixin import TenantAwareBrandingMixin


class LayoutContextMixin(TenantAwareBrandingMixin, LayoutUrlsMixin, BaseTenantAwareMixin):
    """ Build shared layout context for public storefront pages and runtime views. """

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
