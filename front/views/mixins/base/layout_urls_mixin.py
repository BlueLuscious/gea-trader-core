""" Shared storefront URL helpers for public layout context. """

from django.urls import reverse


class LayoutUrlsMixin:
    """ Build shared storefront route URLs for public layout consumers. """

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
