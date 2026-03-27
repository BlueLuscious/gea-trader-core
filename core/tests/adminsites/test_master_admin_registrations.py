""" Tests for master admin site model registrations. """

from django.contrib.auth.models import Group
from django.test import RequestFactory
from accounts.models import UserModel
from cart.models import CartItemModel, CartModel
from catalog.models import ProductImageModel, ProductModel, ProductVariantModel
from core.adminsites.site_instances import master_admin_site
from core.testing.base import LoggedSimpleTestCase
from masterdata.models import BrandModel, CategoryModel
from quotation.models import QuoteItemModel, QuoteModel


class TestMasterAdminRegistrations(LoggedSimpleTestCase):
    """ Verify that master admin registrations stay wired to the shared site. """

    def setUp(self) -> None:
        """ Create the request factory and authenticated superuser used by the tests. """
        self.request_factory = RequestFactory()
        self.superuser = type(
            "SuperUser",
            (),
            {
                "is_active": True,
                "is_superuser": True,
                "is_staff": True,
                "has_module_perms": lambda self, app_label: True,
                "has_perm": lambda self, perm: True,
            },
        )()

    def test_master_admin_registers_expected_domain_models(self) -> None:
        """ Verify the master admin site keeps the expected domain models registered. """
        expected_models = {
            UserModel,
            Group,
            BrandModel,
            CategoryModel,
            ProductModel,
            ProductVariantModel,
            ProductImageModel,
            CartModel,
            CartItemModel,
            QuoteModel,
            QuoteItemModel,
        }

        self.assertTrue(expected_models.issubset(set(master_admin_site._registry)))

    def test_master_admin_sidebar_navigation_includes_registered_domain_model_links(self) -> None:
        """ Verify the dynamic master sidebar exposes links for registered domain models. """
        request = self.request_factory.get("/admin/")
        request.user = self.superuser
        navigation = master_admin_site.get_sidebar_navigation(request)

        item_links = {
            item["link"]
            for group in navigation
            for item in group["items"]
        }

        expected_links = {
            "/admin/accounts/usermodel/",
            "/admin/auth/group/",
            "/admin/masterdata/brandmodel/",
            "/admin/masterdata/categorymodel/",
            "/admin/catalog/productmodel/",
            "/admin/catalog/productvariantmodel/",
            "/admin/catalog/productimagemodel/",
            "/admin/cart/cartmodel/",
            "/admin/cart/cartitemmodel/",
            "/admin/quotation/quotemodel/",
            "/admin/quotation/quoteitemmodel/",
        }

        self.assertTrue(expected_links.issubset(item_links))
