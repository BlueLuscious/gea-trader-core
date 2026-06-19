""" Tests for cart lifecycle tasks. """

from unittest.mock import MagicMock, patch
from core.testing.base import LoggedSimpleTestCase
from cart.tasks import close_expired_carts_task


class TestCartLifecycleTasks(LoggedSimpleTestCase):
    """ Verify cart lifecycle task wrappers. """

    @patch("cart.tasks.lifecycle.tasks.CartExpirationService.close_expired_carts")
    def test_close_expired_carts_task_delegates_to_the_expiration_service(self, close_expired_carts: MagicMock) -> None:
        """ Verify the task delegates expired-cart closure to the domain service. """
        close_expired_carts.return_value = 3

        closed_count = close_expired_carts_task()

        self.assertEqual(3, closed_count)
        close_expired_carts.assert_called_once_with()
