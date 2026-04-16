from django.contrib.auth import get_user_model
from core.testing.base import LoggedTestCase
from cart.choices import CartStatus
from cart.models import CartItemModel, CartModel
from catalog.models import ProductModel, ProductVariantModel
from tenancy.models import TenantModel


class TestCartQuerySet(LoggedTestCase):
    """ Cover cart queryset helpers. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for catalog-linked cart fixtures.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_cart_queryset_filters_status_session_and_user(self) -> None:
        """ Verify CartModelQuerySet filters by lifecycle status and owner. """
        user = get_user_model().objects.create(username='client')
        tenant = self._create_tenant("cart-queryset-status")
        other_tenant = self._create_tenant("cart-queryset-status-other")
        active_cart = CartModel.objects.create(tenant=tenant, session_key='session-1', status=CartStatus.ACTIVE)
        CartModel.objects.create(tenant=tenant, session_key='session-2', status=CartStatus.CONVERTED)
        user_cart = CartModel.objects.create(tenant=tenant, user=user, status=CartStatus.ACTIVE)
        CartModel.objects.create(tenant=other_tenant, session_key='session-9', status=CartStatus.ACTIVE)

        queryset = CartModel.objects.get_queryset().for_tenant(tenant).active().for_user(user)

        self.assertQuerySetEqual(queryset, [user_cart], transform=lambda instance: instance)
        self.assertQuerySetEqual(
            CartModel.objects.get_queryset().for_tenant(tenant).for_session('session-1'),
            [active_cart],
            transform=lambda instance: instance,
        )

    def test_cart_item_queryset_filters_by_cart_and_selects_catalog(self) -> None:
        """ Verify CartItemModelQuerySet filters by cart and eager loads catalog relations. """
        tenant = self._create_tenant("cart-queryset")
        other_tenant = self._create_tenant("cart-queryset-other")
        cart = CartModel.objects.create(tenant=tenant, session_key='session-3')
        other_cart = CartModel.objects.create(tenant=other_tenant, session_key='session-4')
        product = ProductModel.objects.create(tenant=tenant, name='Cartucho', slug='cartucho')
        variant = ProductVariantModel.objects.create(product=product, sku='CAR-001')
        item = CartItemModel.objects.create(cart=cart, product=product, variant=variant, quantity=1)
        other_product = ProductModel.objects.create(tenant=other_tenant, name='Sello', slug='sello')
        CartItemModel.objects.create(cart=other_cart, product=other_product, quantity=1)

        queryset = CartItemModel.objects.get_queryset().for_tenant(tenant).with_catalog().for_cart(cart)

        self.assertQuerySetEqual(queryset, [item], transform=lambda instance: instance)
        self.assertIn('product', queryset.query.select_related)
        self.assertIn('variant', queryset.query.select_related)
