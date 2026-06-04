""" Owner admin tests for tenant-scoped catalog flows. """

from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth.models import Permission
from django.test import RequestFactory
from django.utils.translation import override
from accounts.models import UserModel
from catalog.admin.owner.product_image_model_inline import ProductImageModelInline
from catalog.admin.owner.product_model_admin import ProductModelAdmin
from catalog.admin.owner.product_model_admin_form import ProductModelAdminForm
from catalog.admin.owner.product_variant_model_inline import ProductVariantModelInline
from catalog.models import ProductModel, ProductVariantModel
from core.adminsites.site_instances import owner_admin_site
from core.forms import JsonKeyValueWidget
from core.testing.base import LoggedTestCase
from masterdata.models import BrandModel, CategoryModel
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestOwnerCatalogAdmin(LoggedTestCase):
    """ Verify the owner catalog admin stays scoped to the active tenant. """

    def setUp(self) -> None:
        """ Create reusable request factory, tenant, owner, and product fixtures. """
        self.request_factory = RequestFactory()
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        self.operator = UserModel.objects.create_user(
            username="catalog-operator",
            password="test-pass",
            is_active=True,
            is_staff=True,
        )
        self.outsider = UserModel.objects.create_user(
            username="catalog-outsider",
            password="test-pass",
            is_active=True,
            is_staff=True,
        )
        TenantMembershipModel.objects.create(
            tenant=self.tenant,
            user=self.operator,
            role=TenantRole.OPERATOR,
            is_active=True,
            is_primary=True,
        )
        self.operator.user_permissions.set(
            Permission.objects.filter(
                codename__in=("view_productmodel", "add_productmodel", "change_productmodel")
            )
        )
        self.brand = BrandModel.objects.create(tenant=self.tenant, name="Brand", slug="brand")
        self.category = CategoryModel.objects.create(tenant=self.tenant, name="Category", slug="category")
        self.in_scope_product = ProductModel.objects.create(
            tenant=self.tenant,
            brand=self.brand,
            category=self.category,
            name="Pump",
            slug="pump",
        )
        self.out_of_scope_product = ProductModel.objects.create(
            tenant=self.other_tenant,
            brand=self.brand,
            category=self.category,
            name="Filter",
            slug="filter",
        )
        self.admin = ProductModelAdmin(ProductModel, owner_admin_site)

    def build_request(self, user: UserModel, tenant: TenantModel | None) -> object:
        """ Build one owner-admin request for one user and tenant context.

        Args:
            user: Authenticated actor.
            tenant: Active tenant in scope.

        Returns:
            object: Request object carrying the actor and tenant.
        """
        request = self.request_factory.get("/owner-admin/catalog/productmodel/")
        request.user = user
        request.tenant = tenant
        return request

    def build_variant_formset(
        self,
        data: dict[str, str],
        instance: ProductModel | None = None,
    ) -> object:
        """ Build the owner variant inline formset with one realistic POST payload.

        Args:
            data: Bound inline POST payload.
            instance: Product instance bound to the inline formset.

        Returns:
            object: Bound variant inline formset.
        """
        inline = ProductVariantModelInline(ProductModel, owner_admin_site)
        request = self.request_factory.post("/owner-admin/catalog/productmodel/add/")
        request.user = self.operator
        request.tenant = self.tenant
        formset_class = inline.get_formset(request, obj=instance)
        prefix = formset_class.get_default_prefix()
        product = instance or ProductModel(
            tenant=self.tenant,
            brand=self.brand,
            category=self.category,
            name="Draft product",
            slug="draft-product",
        )
        normalized_data = {
            key.replace("variants-", f"{prefix}-", 1): value
            for key, value in data.items()
        }
        return formset_class(data=normalized_data, instance=product, prefix=prefix)

    def build_empty_variant_form(self, instance: ProductModel) -> object:
        """ Build the empty owner inline variant form for one existing product.

        Args:
            instance: Product instance that owns the variant inline.

        Returns:
            object: Empty inline variant form bound to the current product context.
        """
        inline = ProductVariantModelInline(ProductModel, owner_admin_site)
        request = self.request_factory.get("/owner-admin/catalog/productmodel/")
        request.user = self.operator
        request.tenant = self.tenant
        formset_class = inline.get_formset(request, obj=instance)
        formset = formset_class(instance=instance)
        return formset.empty_form

    def test_get_queryset_is_scoped_to_the_active_tenant(self) -> None:
        """ Verify the owner product queryset only returns products from the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        with patch("catalog.admin.owner.product_model_admin.logger.info") as logger_info_mock:
            queryset = self.admin.get_queryset(request)

        self.assertEqual([self.in_scope_product], list(queryset))
        logger_info_mock.assert_called_once()

    def test_save_model_assigns_the_active_tenant_on_create(self) -> None:
        """ Verify owner-created products inherit the active tenant automatically. """
        request = self.build_request(self.operator, self.tenant)
        product = ProductModel(
            brand=self.brand,
            category=self.category,
            name="Valve",
            slug="valve",
        )
        form = ProductModelAdmin.form(instance=product)

        with patch("catalog.admin.owner.product_model_admin.logger.info") as logger_info_mock:
            self.admin.save_model(request, product, form, change=False)

        self.assertEqual(self.tenant, product.tenant)
        logger_info_mock.assert_called_once()

    def test_product_form_requires_base_sku(self) -> None:
        """ Verify owner product forms require one product-family SKU. """
        form = ProductModelAdminForm(
            data={
                "tenant": str(self.tenant.pk),
                "name": "Valve",
                "slug": "valve",
                "sku_base": "",
                "is_active": "on",
                "requires_quote": "on",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("sku_base", form.errors)

    def test_view_and_change_permissions_reject_products_from_other_tenants(self) -> None:
        """ Verify object permissions stay scoped to products owned by the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(self.admin.has_view_permission(request, self.in_scope_product))
        self.assertTrue(self.admin.has_change_permission(request, self.in_scope_product))
        self.assertFalse(self.admin.has_view_permission(request, self.out_of_scope_product))
        self.assertFalse(self.admin.has_change_permission(request, self.out_of_scope_product))

    def test_module_and_add_permissions_require_catalog_access(self) -> None:
        """ Verify catalog module and add access stay blocked without tenant membership. """
        member_request = self.build_request(self.operator, self.tenant)
        outsider_request = self.build_request(self.outsider, self.tenant)

        self.assertTrue(self.admin.has_module_permission(member_request))
        self.assertTrue(self.admin.has_add_permission(member_request))
        self.assertFalse(self.admin.has_module_permission(outsider_request))
        self.assertFalse(self.admin.has_add_permission(outsider_request))

    def test_image_inline_logs_variant_queryset_construction_for_the_current_product(self) -> None:
        """ Verify the owner image inline logs variant choices scoped to the current product. """
        inline = ProductImageModelInline(ProductModel, owner_admin_site)
        request = self.build_request(self.operator, self.tenant)

        with patch("catalog.admin.owner.product_image_model_inline_formset.logger.info") as logger_info_mock:
            formset_class = inline.get_formset(request, obj=self.in_scope_product)
            formset = formset_class(instance=self.in_scope_product)
            formset.empty_form.fields["variant"].queryset.count()

        logger_info_mock.assert_called_once()

    def test_variant_inline_requires_at_least_one_variant(self) -> None:
        """ Verify owner products cannot be saved without at least one variant. """
        with override("en"):
            formset = self.build_variant_formset(
                data={
                    "variants-TOTAL_FORMS": "0",
                    "variants-INITIAL_FORMS": "0",
                    "variants-MIN_NUM_FORMS": "0",
                    "variants-MAX_NUM_FORMS": "1000",
                }
            )

            self.assertFalse(formset.is_valid())
            self.assertIn("Add at least one variant before saving the product.", formset.non_form_errors())

    def test_variant_inline_requires_one_default_variant(self) -> None:
        """ Verify owner products cannot be saved when no default variant is selected. """
        with override("en"):
            formset = self.build_variant_formset(
                data={
                    "variants-TOTAL_FORMS": "1",
                    "variants-INITIAL_FORMS": "0",
                    "variants-MIN_NUM_FORMS": "0",
                    "variants-MAX_NUM_FORMS": "1000",
                    "variants-0-name": "Standard",
                    "variants-0-sku": "PUMP-001",
                    "variants-0-price": "15.00",
                    "variants-0-is_active": "on",
                    "variants-0-sort_order": "0",
                }
            )

            self.assertFalse(formset.is_valid())
            self.assertIn("Choose exactly one default variant for this product.", formset.non_form_errors())

    def test_variant_inline_rejects_multiple_default_variants(self) -> None:
        """ Verify owner products cannot be saved with more than one default variant. """
        with override("en"):
            formset = self.build_variant_formset(
                data={
                    "variants-TOTAL_FORMS": "2",
                    "variants-INITIAL_FORMS": "0",
                    "variants-MIN_NUM_FORMS": "0",
                    "variants-MAX_NUM_FORMS": "1000",
                    "variants-0-name": "Primary",
                    "variants-0-sku": "PUMP-001",
                    "variants-0-price": "15.00",
                    "variants-0-is_default": "on",
                    "variants-0-is_active": "on",
                    "variants-0-sort_order": "0",
                    "variants-1-name": "Secondary",
                    "variants-1-sku": "PUMP-002",
                    "variants-1-price": "18.00",
                    "variants-1-is_default": "on",
                    "variants-1-is_active": "on",
                    "variants-1-sort_order": "1",
                }
            )

            self.assertFalse(formset.is_valid())
            self.assertIn("Choose exactly one default variant for this product.", formset.non_form_errors())

    def test_variant_inline_accepts_one_default_variant(self) -> None:
        """ Verify owner products can be saved when exactly one default variant exists. """
        formset = self.build_variant_formset(
            data={
                "variants-TOTAL_FORMS": "2",
                "variants-INITIAL_FORMS": "0",
                "variants-MIN_NUM_FORMS": "0",
                "variants-MAX_NUM_FORMS": "1000",
                "variants-0-name": "Primary",
                "variants-0-sku": "PUMP-001",
                "variants-0-price": str(Decimal("15.00")),
                "variants-0-is_default": "on",
                "variants-0-is_active": "on",
                "variants-0-sort_order": "0",
                "variants-1-name": "Secondary",
                "variants-1-sku": "PUMP-002",
                "variants-1-price": str(Decimal("18.00")),
                "variants-1-is_active": "on",
                "variants-1-sort_order": "1",
            }
        )

        self.assertTrue(
            formset.is_valid(),
            f"errors={formset.errors} non_form_errors={formset.non_form_errors()}",
        )

    def test_variant_inline_explains_quote_only_price_behavior(self) -> None:
        """ Verify quote-only products explain that variant prices stay internal and optional. """
        with override("en"):
            quote_only_product = ProductModel.objects.create(
                tenant=self.tenant,
                brand=self.brand,
                category=self.category,
                name="Quote-only pump",
                slug="quote-only-pump",
                requires_quote=True,
            )

            empty_form = self.build_empty_variant_form(quote_only_product)

            self.assertEqual(
                "Optional internal price. Customers still request a quote for this product.",
                empty_form.fields["price"].help_text,
            )

    def test_variant_inline_exposes_the_attributes_editor(self) -> None:
        """ Verify owner variant forms expose the key-value attributes editor. """
        empty_form = self.build_empty_variant_form(self.in_scope_product)

        self.assertIn("attributes_json", empty_form.fields)
        self.assertIsInstance(empty_form.fields["attributes_json"].widget, JsonKeyValueWidget)

    def test_variant_inline_persists_submitted_attributes(self) -> None:
        """ Verify owner variant rows persist key-value attributes as a JSON dictionary. """
        self.operator.user_permissions.add(Permission.objects.get(codename="add_productvariantmodel"))
        formset = self.build_variant_formset(
            data={
                "variants-TOTAL_FORMS": "1",
                "variants-INITIAL_FORMS": "0",
                "variants-MIN_NUM_FORMS": "0",
                "variants-MAX_NUM_FORMS": "1000",
                "variants-0-name": "Primary",
                "variants-0-sku": "PUMP-ATTR-001",
                "variants-0-attributes_json__key": "capacidad",
                "variants-0-attributes_json__value": "20L",
                "variants-0-price": str(Decimal("15.00")),
                "variants-0-is_default": "on",
                "variants-0-is_active": "on",
                "variants-0-sort_order": "0",
            },
            instance=self.in_scope_product,
        )

        self.assertTrue(
            formset.is_valid(),
            f"errors={formset.errors} non_form_errors={formset.non_form_errors()}",
        )
        formset.save()

        variant = ProductVariantModel.objects.get(product=self.in_scope_product, sku="PUMP-ATTR-001")
        self.assertEqual(variant.attributes_json, {"capacidad": "20L"})

    def test_variant_inline_clears_submitted_empty_attributes(self) -> None:
        """ Verify owner variant rows clear attributes when the editor is submitted empty. """
        self.operator.user_permissions.add(Permission.objects.get(codename="change_productvariantmodel"))
        variant = ProductVariantModel.objects.create(
            product=self.in_scope_product,
            name="Primary",
            sku="PUMP-CLEAR-001",
            attributes_json={"capacidad": "20L"},
            price=Decimal("15.00"),
            is_default=True,
            is_active=True,
            sort_order=0,
        )
        formset = self.build_variant_formset(
            data={
                "variants-TOTAL_FORMS": "1",
                "variants-INITIAL_FORMS": "1",
                "variants-MIN_NUM_FORMS": "0",
                "variants-MAX_NUM_FORMS": "1000",
                "variants-0-id": str(variant.pk),
                "variants-0-name": "Primary",
                "variants-0-sku": "PUMP-CLEAR-001",
                "variants-0-attributes_json__present": "1",
                "variants-0-price": str(Decimal("15.00")),
                "variants-0-is_default": "on",
                "variants-0-is_active": "on",
                "variants-0-sort_order": "0",
            },
            instance=self.in_scope_product,
        )

        self.assertTrue(
            formset.is_valid(),
            f"errors={formset.errors} non_form_errors={formset.non_form_errors()}",
        )
        self.assertEqual(formset.forms[0].cleaned_data["attributes_json"], {})
        self.assertIn("attributes_json", formset.forms[0].changed_data)
        self.assertEqual(formset.forms[0].instance.attributes_json, {})
        saved_instances = formset.save()
        variant.refresh_from_db()

        self.assertEqual([instance.pk for instance in saved_instances], [variant.pk])
        self.assertEqual(saved_instances[0].attributes_json, {})
        self.assertEqual(variant.attributes_json, {})

    def test_variant_inline_explains_purchasable_default_price_requirement(self) -> None:
        """ Verify purchasable products explain the priced default-variant rule before save. """
        with override("en"):
            purchasable_product = ProductModel.objects.create(
                tenant=self.tenant,
                brand=self.brand,
                category=self.category,
                name="Purchasable pump",
                slug="purchasable-pump",
                requires_quote=False,
            )

            empty_form = self.build_empty_variant_form(purchasable_product)

            self.assertEqual(
                "Required on the default variant when the product is directly purchasable.",
                empty_form.fields["price"].help_text,
            )

    def test_variant_inline_requires_a_priced_default_variant_for_purchasable_products(self) -> None:
        """ Verify purchasable products need a price on the default variant. """
        with override("en"):
            formset = self.build_variant_formset(
                data={
                    "variants-TOTAL_FORMS": "1",
                    "variants-INITIAL_FORMS": "0",
                    "variants-MIN_NUM_FORMS": "0",
                    "variants-MAX_NUM_FORMS": "1000",
                    "variants-0-name": "Primary",
                    "variants-0-sku": "PUMP-003",
                    "variants-0-is_default": "on",
                    "variants-0-is_active": "on",
                    "variants-0-sort_order": "0",
                }
            )

            self.assertFalse(formset.is_valid())
            self.assertIn("Purchasable products require a price on the default variant.", formset.non_form_errors())

    def test_variant_inline_allows_an_unpriced_default_variant_for_quote_only_products(self) -> None:
        """ Verify quote-only products may keep the default variant price empty. """
        formset = self.build_variant_formset(
            data={
                "requires_quote": "on",
                "variants-TOTAL_FORMS": "1",
                "variants-INITIAL_FORMS": "0",
                "variants-MIN_NUM_FORMS": "0",
                "variants-MAX_NUM_FORMS": "1000",
                "variants-0-name": "Primary",
                "variants-0-sku": "PUMP-004",
                "variants-0-is_default": "on",
                "variants-0-is_active": "on",
                "variants-0-sort_order": "0",
            }
        )

        self.assertTrue(
            formset.is_valid(),
            f"errors={formset.errors} non_form_errors={formset.non_form_errors()}",
        )

    def test_variant_inline_rejects_an_inactive_default_variant(self) -> None:
        """ Verify owner products cannot keep the default variant unavailable for selection. """
        with override("en"):
            formset = self.build_variant_formset(
                data={
                    "variants-TOTAL_FORMS": "1",
                    "variants-INITIAL_FORMS": "0",
                    "variants-MIN_NUM_FORMS": "0",
                    "variants-MAX_NUM_FORMS": "1000",
                    "variants-0-name": "Primary",
                    "variants-0-sku": "PUMP-005",
                    "variants-0-price": "15.00",
                    "variants-0-is_default": "on",
                    "variants-0-sort_order": "0",
                }
            )

            self.assertFalse(formset.is_valid())
            self.assertIn("The default variant must stay available for selection.", formset.non_form_errors())
