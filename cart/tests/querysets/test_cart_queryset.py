from django.contrib.auth import get_user_model
from core.testing.base import LoggedTestCase
from cart.choices import CartStatus
from cart.models import CartItemModel, CartModel
from catalog.models import ProductModel, ProductVariantModel


class TestCartQuerySet(LoggedTestCase):
    """ Cover cart queryset helpers. """

    def test_cart_queryset_filters_status_session_and_user(self) -> None:
        """ Verify CartModelQuerySet filters by lifecycle status and owner. """
        user = get_user_model().objects.create(username='client')
        active_cart = CartModel.objects.create(session_key='session-1', status=CartStatus.ACTIVE)
        CartModel.objects.create(session_key='session-2', status=CartStatus.CONVERTED)
        user_cart = CartModel.objects.create(user=user, status=CartStatus.ACTIVE)

        queryset = CartModel.objects.get_queryset().active().for_user(user)

        self.assertQuerySetEqual(queryset, [user_cart], transform=lambda instance: instance)
        self.assertIn(active_cart, list(CartModel.objects.get_queryset().for_session('session-1')))

    def test_cart_item_queryset_filters_by_cart_and_selects_catalog(self) -> None:
        """ Verify CartItemModelQuerySet filters by cart and eager loads catalog relations. """
        cart = CartModel.objects.create(session_key='session-3')
        product = ProductModel.objects.create(name='Cartucho', slug='cartucho')
        variant = ProductVariantModel.objects.create(product=product, sku='CAR-001')
        item = CartItemModel.objects.create(cart=cart, product=product, variant=variant, quantity=1)

        queryset = CartItemModel.objects.get_queryset().with_catalog().for_cart(cart)

        self.assertQuerySetEqual(queryset, [item], transform=lambda instance: instance)
        self.assertIn('product', queryset.query.select_related)
        self.assertIn('variant', queryset.query.select_related)
