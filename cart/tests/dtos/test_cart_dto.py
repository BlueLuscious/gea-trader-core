from dataclasses import FrozenInstanceError
from django.utils import timezone
from core.testing.base import LoggedSimpleTestCase
from cart.dtos import CartItemModelDTO, CartModelDTO


class TestCartDTO(LoggedSimpleTestCase):
    """ Cover cart DTO objects. """

    def test_cart_model_dto_is_frozen(self) -> None:
        """ Verify CartModelDTO behaves as an immutable dataclass. """
        dto = CartModelDTO(
            id=1,
            user_id=None,
            session_key='session-1',
            status='active',
            expires_at=None,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        with self.assertRaises(FrozenInstanceError):
            dto.status = 'converted'

    def test_cart_item_model_dto_stores_quantity_and_notes(self) -> None:
        """ Verify CartItemModelDTO keeps quantity and notes values. """
        dto = CartItemModelDTO(
            id=2,
            cart_id=1,
            product_id=3,
            variant_id=None,
            quantity=4,
            notes='Urgente',
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        self.assertEqual(dto.quantity, 4)
        self.assertEqual(dto.notes, 'Urgente')
