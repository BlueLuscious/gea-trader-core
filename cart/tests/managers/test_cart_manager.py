from django.contrib.auth import get_user_model
from core.testing.base import LoggedTestCase
from cart.choices import CartStatus
from cart.models import CartItemModel, CartModel
from catalog.models import ProductModel, ProductVariantModel
from tenancy.models import TenantModel


class TestCartManager(LoggedTestCase):
    """ Cover cart manager helpers. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for catalog-linked cart fixtures.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_cart_manager_filters_by_status_session_and_user(self) -> None:
        """ Verify cart manager helpers return the expected cart subsets. """
        user = get_user_model().objects.create(username='owner')
        active_cart = CartModel.objects.create(session_key='session-1', status=CartStatus.ACTIVE)
        converted_cart = CartModel.objects.create(session_key='session-2', status=CartStatus.CONVERTED)
        abandoned_cart = CartModel.objects.create(user=user, status=CartStatus.ABANDONED)

        self.assertQuerySetEqual(CartModel.objects.active(), [active_cart], transform=lambda instance: instance)
        self.assertQuerySetEqual(CartModel.objects.converted(), [converted_cart], transform=lambda instance: instance)
        self.assertQuerySetEqual(CartModel.objects.abandoned(), [abandoned_cart], transform=lambda instance: instance)
        self.assertQuerySetEqual(CartModel.objects.for_session('session-1'), [active_cart], transform=lambda instance: instance)
        self.assertQuerySetEqual(CartModel.objects.for_user(user), [abandoned_cart], transform=lambda instance: instance)

    def test_cart_item_manager_helpers_filter_and_select_related(self) -> None:
        """ Verify cart item manager helpers return cart subsets with catalog data. """
        cart = CartModel.objects.create(session_key='session-3')
        other_cart = CartModel.objects.create(session_key='session-4')
        tenant = self._create_tenant("cart-manager")
        product = ProductModel.objects.create(tenant=tenant, name='Valvula', slug='valvula')
        variant = ProductVariantModel.objects.create(product=product, sku='VAL-001')
        matching_item = CartItemModel.objects.create(cart=cart, product=product, variant=variant, quantity=2)
        CartItemModel.objects.create(cart=other_cart, product=product, variant=variant, quantity=1)

        self.assertQuerySetEqual(CartItemModel.objects.for_cart(cart), [matching_item], transform=lambda instance: instance)
        self.assertIn('product', CartItemModel.objects.with_catalog().query.select_related)
        self.assertIn('variant', CartItemModel.objects.with_catalog().query.select_related)
