from django.db import IntegrityError, transaction
from core.testing.base import LoggedTestCase
from cart.models import CartItemModel, CartModel
from catalog.models import ProductModel, ProductVariantModel
from tenancy.models import TenantModel


class TestCartModel(LoggedTestCase):
    """ Cover cart model behavior. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for catalog-linked cart fixtures.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_cart_and_items_relationships_and_strings(self) -> None:
        """ Verify cart relationships and string representations. """
        cart = CartModel.objects.create(session_key='session-1')
        tenant = self._create_tenant("cart-model")
        product = ProductModel.objects.create(tenant=tenant, name='Filtro', slug='filtro')
        variant = ProductVariantModel.objects.create(product=product, sku='FIL-001')
        item = CartItemModel.objects.create(cart=cart, product=product, variant=variant, quantity=2)

        self.assertEqual(item.cart, cart)
        self.assertEqual(str(cart), f'Cart {cart.pk}')
        self.assertEqual(str(item), f'Cart item {item.pk}')

    def test_cart_requires_user_or_session_key(self) -> None:
        """ Verify the cart constraint rejects rows without user and session key. """
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CartModel.objects.create()

    def test_cart_item_unique_constraints_are_enforced(self) -> None:
        """ Verify duplicate cart items for the same product and variant are rejected. """
        cart = CartModel.objects.create(session_key='session-2')
        tenant = self._create_tenant("cart-unique")
        product = ProductModel.objects.create(tenant=tenant, name='Bomba', slug='bomba')
        variant = ProductVariantModel.objects.create(product=product, sku='BOM-001')
        CartItemModel.objects.create(cart=cart, product=product, variant=variant, quantity=1)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CartItemModel.objects.create(cart=cart, product=product, variant=variant, quantity=1)
