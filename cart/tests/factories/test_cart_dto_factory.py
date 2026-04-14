from core.testing.base import LoggedTestCase
from cart.dtos.factories import CartItemModelDTOFactory, CartModelDTOFactory
from cart.models import CartItemModel, CartModel
from catalog.models import ProductModel, ProductVariantModel


class TestCartDTOFactory(LoggedTestCase):
    """ Cover cart DTO factories. """

    def test_cart_model_dto_factory_build_maps_fields(self) -> None:
        """ Verify CartModelDTOFactory.build maps cart fields. """
        cart = CartModel.objects.create(session_key='session-1')

        dto = CartModelDTOFactory.build(cart)

        self.assertEqual(dto.id, cart.id)
        self.assertEqual(dto.session_key, 'session-1')
        self.assertEqual(dto.status, cart.status)

    def test_cart_item_model_dto_factory_build_many_returns_all_items(self) -> None:
        """ Verify CartItemModelDTOFactory.build_many returns DTOs for each item. """
        cart = CartModel.objects.create(session_key='session-2')
        product = ProductModel.objects.create(name='Bomba', slug='bomba')
        variant = ProductVariantModel.objects.create(product=product, sku='BOM-001')
        first = CartItemModel.objects.create(cart=cart, product=product, variant=variant, quantity=1)
        second = CartItemModel.objects.create(cart=cart, product=product, quantity=2)

        dtos = CartItemModelDTOFactory.build_many([first, second])

        self.assertEqual([dto.quantity for dto in dtos], [1, 2])
        self.assertEqual([dto.product_id for dto in dtos], [product.id, product.id])
