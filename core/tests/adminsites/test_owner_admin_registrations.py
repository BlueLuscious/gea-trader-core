""" Tests for owner admin site model registrations. """

from django.contrib.auth.models import Permission
from django.test import RequestFactory
from catalog.admin.owner.product_image_model_inline import ProductImageModelInline
from catalog.admin.owner.product_model_admin import ProductModelAdmin
from catalog.admin.owner.product_variant_model_inline import ProductVariantModelInline
from catalog.models import ProductModel
from core.adminsites.site_instances import owner_admin_site
from core.testing.base import LoggedTestCase
from catalog.models import ProductVariantModel
from masterdata.models import BrandModel, CategoryModel


class TestOwnerAdminRegistrations(LoggedTestCase):
    """ Verify that owner admin registrations stay limited to the curated surface. """

    def setUp(self) -> None:
        """ Create the request factory and authenticated owner used by the tests. """
        self.request_factory = RequestFactory()
        self.owner_user = type(
            "OwnerUser",
            (),
            {
                "is_active": True,
                "is_superuser": False,
                "is_staff": True,
                "has_module_perms": lambda self, app_label: True,
                "has_perm": lambda self, perm: True,
            },
        )()

    def test_owner_admin_registers_products_only_for_now(self) -> None:
        """ Verify the owner admin site currently registers the product model. """
        self.assertIn(ProductModel, owner_admin_site._registry)

    def test_owner_admin_sidebar_navigation_includes_registered_product_link(self) -> None:
        """ Verify the owner sidebar exposes the registered product changelist link. """
        request = self.request_factory.get("/owner-admin/")
        request.user = self.owner_user
        navigation = owner_admin_site.get_sidebar_navigation(request)

        item_links = {
            item["link"]
            for group in navigation
            for item in group["items"]
        }

        self.assertIn("/owner-admin/catalog/productmodel/", item_links)

    def test_owner_products_flow_requires_expected_django_permissions(self) -> None:
        """ Verify the owner products flow is backed by the expected Django model permissions. """
        expected_permissions = {
            "add_productmodel",
            "change_productmodel",
            "view_productmodel",
            "add_productvariantmodel",
            "change_productvariantmodel",
            "view_productvariantmodel",
            "add_productimagemodel",
            "change_productimagemodel",
            "delete_productimagemodel",
            "view_productimagemodel",
        }

        found_permissions = set(
            Permission.objects.filter(
                codename__in=expected_permissions,
                content_type__app_label="catalog",
            ).values_list("codename", flat=True)
        )

        self.assertEqual(expected_permissions, found_permissions)

    def test_owner_product_image_inline_limits_variant_choices_to_current_product(self) -> None:
        """ Verify the image inline only exposes variants belonging to the current product. """
        brand = BrandModel.objects.create(name="Brand", slug="brand")
        category = CategoryModel.objects.create(name="Category", slug="category")
        first_product = ProductModel.objects.create(name="First", slug="first", brand=brand, category=category)
        second_product = ProductModel.objects.create(name="Second", slug="second", brand=brand, category=category)
        first_variant = ProductVariantModel.objects.create(product=first_product, sku="FIRST-1")
        ProductVariantModel.objects.create(product=second_product, sku="SECOND-1")

        inline = ProductImageModelInline(ProductModel, owner_admin_site)
        request = self.request_factory.get("/owner-admin/catalog/productmodel/")
        request.user = self.owner_user

        formset_class = inline.get_formset(request, obj=first_product)
        formset = formset_class(instance=first_product)
        variant_queryset = formset.empty_form.fields["variant"].queryset

        self.assertEqual([first_variant], list(variant_queryset))

    def test_owner_product_admin_prefers_guided_delete_policy(self) -> None:
        """ Verify the owner products flow disables hard delete where soft state already exists. """
        product_admin = ProductModelAdmin(ProductModel, owner_admin_site)
        variant_inline = ProductVariantModelInline(ProductModel, owner_admin_site)
        image_inline = ProductImageModelInline(ProductModel, owner_admin_site)

        request = self.request_factory.get("/owner-admin/catalog/productmodel/")
        request.user = self.owner_user

        self.assertFalse(product_admin.has_delete_permission(request))
        self.assertFalse(variant_inline.can_delete)
        self.assertTrue(image_inline.can_delete)

    def test_owner_product_admin_uses_tabs_for_sections_and_inline_workflows(self) -> None:
        """ Verify the owner product admin uses Unfold tabs for a more guided layout. """
        product_admin = ProductModelAdmin(ProductModel, owner_admin_site)

        fieldset_classes = [fieldset[1].get("classes", ()) for fieldset in product_admin.fieldsets]

        self.assertIn(("tab",), fieldset_classes)
        self.assertEqual(4, fieldset_classes.count(("tab",)))
        self.assertTrue(ProductVariantModelInline.tab)
        self.assertTrue(ProductImageModelInline.tab)

    def test_owner_product_admin_loads_custom_css_for_fieldset_description_spacing(self) -> None:
        """ Verify the owner product admin loads the CSS tweak for fieldset descriptions. """
        product_admin = ProductModelAdmin(ProductModel, owner_admin_site)

        self.assertIn(
            "catalog/admin/owner/product_model_admin.css",
            str(product_admin.media),
        )
