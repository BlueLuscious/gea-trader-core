from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from django.utils.translation import override
from core.testing.base import LoggedTestCase
from catalog.models import ProductImageModel, ProductModel, ProductVariantModel
from masterdata.models import BrandModel, CategoryModel
from tenancy.models import TenantModel


class TestCatalogModel(LoggedTestCase):
    """ Cover catalog model behavior. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for product ownership tests.

        Args:
            slug: Stable slug for the tenant.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_product_variant_and_image_relationships(self) -> None:
        """ Verify catalog relations between product, variant and image. """
        tenant = self._create_tenant("gea")
        brand = BrandModel.objects.create(tenant=tenant, name="GEA", slug="gea")
        category = CategoryModel.objects.create(tenant=tenant, name="Lubricacion", slug="lubricacion")
        product = ProductModel.objects.create(tenant=tenant, brand=brand, category=category, name="Aceite termico", slug="aceite-termico")
        variant = ProductVariantModel.objects.create(product=product, sku="ACE-001", attributes_json={"viscosidad": "46"}, is_default=True)
        image = ProductImageModel.objects.create(product=product, variant=variant, image=SimpleUploadedFile("aceite.jpg", b"binary", content_type="image/jpeg"), alt_text="Aceite termico", is_primary=True)

        self.assertEqual(product.tenant, tenant)
        self.assertEqual(variant.product, product)
        self.assertEqual(image.product, product)
        self.assertEqual(image.variant, variant)

    def test_string_representations_prefer_human_labels(self) -> None:
        """ Verify catalog model string representations are user friendly. """
        tenant = self._create_tenant("north")
        product = ProductModel.objects.create(tenant=tenant, name="Bomba", slug="bomba")
        variant = ProductVariantModel.objects.create(product=product, name="Linea A", sku="BOM-001")
        image = ProductImageModel.objects.create(product=product, image=SimpleUploadedFile("bomba.jpg", b"binary", content_type="image/jpeg"), alt_text="Bomba frontal")

        self.assertEqual(str(product), "Bomba")
        self.assertEqual(str(variant), "Linea A")
        self.assertEqual(str(image), "Bomba frontal")

    def test_product_image_rejects_variant_from_another_product(self) -> None:
        """ Verify product images cannot point to a variant owned by another product. """
        tenant = self._create_tenant("image-variant-scope")
        first_product = ProductModel.objects.create(tenant=tenant, name="Pump", slug="pump")
        second_product = ProductModel.objects.create(tenant=tenant, name="Valve", slug="valve")
        foreign_variant = ProductVariantModel.objects.create(
            product=second_product,
            sku="VALVE-001",
        )
        image = ProductImageModel(
            product=first_product,
            variant=foreign_variant,
            image=SimpleUploadedFile("pump.jpg", b"binary", content_type="image/jpeg"),
            alt_text="Pump image",
        )

        with self.assertRaises(ValidationError):
            image.full_clean()

    def test_product_allows_at_most_one_primary_root_image(self) -> None:
        """ Verify one product cannot keep more than one primary root image. """
        tenant = self._create_tenant("image-primary-root")
        product = ProductModel.objects.create(tenant=tenant, name="Pump", slug="pump")
        ProductImageModel.objects.create(
            product=product,
            image=SimpleUploadedFile("pump-primary.jpg", b"binary", content_type="image/jpeg"),
            alt_text="Primary pump image",
            is_primary=True,
        )
        second_primary_image = ProductImageModel(
            product=product,
            image=SimpleUploadedFile("pump-secondary.jpg", b"binary", content_type="image/jpeg"),
            alt_text="Secondary pump image",
            is_primary=True,
        )

        with self.assertRaises(ValidationError):
            second_primary_image.full_clean()

    def test_variant_allows_at_most_one_primary_image(self) -> None:
        """ Verify one variant cannot keep more than one primary image. """
        tenant = self._create_tenant("image-primary-variant")
        product = ProductModel.objects.create(tenant=tenant, name="Pump", slug="pump")
        variant = ProductVariantModel.objects.create(
            product=product,
            sku="PUMP-001",
        )
        ProductImageModel.objects.create(
            product=product,
            variant=variant,
            image=SimpleUploadedFile("pump-variant-primary.jpg", b"binary", content_type="image/jpeg"),
            alt_text="Primary variant image",
            is_primary=True,
        )
        second_primary_variant_image = ProductImageModel(
            product=product,
            variant=variant,
            image=SimpleUploadedFile("pump-variant-secondary.jpg", b"binary", content_type="image/jpeg"),
            alt_text="Secondary variant image",
            is_primary=True,
        )

        with self.assertRaises(ValidationError):
            second_primary_variant_image.full_clean()

    def test_product_slug_can_repeat_across_different_tenants(self) -> None:
        """ Allow the same product slug when each tenant owns a separate catalog. """
        first_tenant = self._create_tenant("north")
        second_tenant = self._create_tenant("south")

        first_product = ProductModel.objects.create(tenant=first_tenant, name="Bomba", slug="bomba")
        second_product = ProductModel.objects.create(tenant=second_tenant, name="Bomba", slug="bomba")

        self.assertEqual(first_product.slug, second_product.slug)

    def test_product_helpers_resolve_default_variant_and_public_price(self) -> None:
        """ Resolve default variant and public price from the variant layer. """
        tenant = self._create_tenant("pricing-default")
        product = ProductModel.objects.create(
            tenant=tenant,
            name="Pump",
            slug="pump",
            requires_quote=False,
        )
        secondary_variant = ProductVariantModel.objects.create(
            product=product,
            name="Secondary",
            sku="PUMP-SECONDARY",
            price=Decimal("22.00"),
            is_default=False,
            sort_order=1,
        )
        default_variant = ProductVariantModel.objects.create(
            product=product,
            name="Default",
            sku="PUMP-DEFAULT",
            price=Decimal("25.00"),
            is_default=True,
            sort_order=0,
        )

        self.assertTrue(product.has_variants())
        self.assertEqual(default_variant, product.get_default_variant())
        self.assertEqual(Decimal("25.00"), product.get_public_price())
        self.assertNotEqual(secondary_variant, product.get_default_variant())

    def test_quote_only_product_hides_public_price_even_when_variant_has_internal_price(self) -> None:
        """ Keep quote-only pricing internal even when the default variant has a price. """
        tenant = self._create_tenant("pricing-quote-only")
        product = ProductModel.objects.create(
            tenant=tenant,
            name="Filter",
            slug="filter",
            requires_quote=True,
        )
        default_variant = ProductVariantModel.objects.create(
            product=product,
            sku="FILTER-DEFAULT",
            price=Decimal("39.90"),
            is_default=True,
        )

        self.assertEqual(default_variant, product.get_default_variant())
        self.assertIsNone(product.get_public_price())

    def test_product_helpers_return_none_when_no_default_variant_exists_yet(self) -> None:
        """ Return no default variant or public price when the product is still incomplete. """
        tenant = self._create_tenant("pricing-no-default")
        product = ProductModel.objects.create(
            tenant=tenant,
            name="Valve",
            slug="valve",
            requires_quote=False,
        )
        ProductVariantModel.objects.create(
            product=product,
            sku="VALVE-001",
            price=Decimal("18.00"),
            is_default=False,
        )

        self.assertTrue(product.has_variants())
        self.assertIsNone(product.get_default_variant())
        self.assertIsNone(product.get_public_price())

    def test_product_helpers_expose_active_variant_count_semantics(self) -> None:
        """ Return active-variant metrics used by public product cards. """
        tenant = self._create_tenant("variant-count")
        product = ProductModel.objects.create(
            tenant=tenant,
            name="Compressor Kit",
            slug="compressor-kit",
        )
        ProductVariantModel.objects.create(product=product, sku="COMP-001", is_active=True)
        ProductVariantModel.objects.create(product=product, sku="COMP-002", is_active=True)
        ProductVariantModel.objects.create(product=product, sku="COMP-003", is_active=False)

        self.assertEqual(2, product.get_active_variant_count())
        self.assertTrue(product.has_multiple_active_variants())

    def test_default_variant_must_stay_active(self) -> None:
        """ Verify one default variant cannot be saved as inactive. """
        tenant = self._create_tenant("variant-default-active")
        product = ProductModel.objects.create(
            tenant=tenant,
            name="Pump",
            slug="pump",
        )
        variant = ProductVariantModel(
            product=product,
            sku="PUMP-DEFAULT",
            is_default=True,
            is_active=False,
        )

        with self.assertRaises(ValidationError):
            variant.full_clean()

    def test_model_field_metadata_uses_friendly_translatable_copy(self) -> None:
        """ Verify catalog model fields expose user-friendly labels and help texts. """
        product_field_expectations = {
            "tenant": ("Tenant", "Tenant that owns this product and its related catalog data."),
            "name": ("Product name", "Customer-facing name shown across the catalog."),
            "slug": ("URL slug", "Short URL-friendly identifier used in product links."),
            "short_description": ("Short description", "Short summary for compact cards and product lists."),
            "requires_quote": ("Request through quote", "Enable this when customers should request a quote instead of buying directly."),
        }
        variant_field_expectations = {
            "sku": ("Variant SKU", "Unique internal reference for this variant."),
            "price": ("Price", "Optional direct price for this variant when it does not rely only on quotes."),
            "is_active": ("Available for selection", "Turn this off to keep the variant without offering it."),
        }
        image_field_expectations = {
            "image": ("Image file", "Upload the product image shown in the catalog and admin."),
            "alt_text": ("Alt text", "Short accessibility description of what appears in the image."),
            "is_primary": ("Primary image", "Use this image as the main visual for the product or variant."),
        }

        with override("en"):
            for field_name, expected_values in product_field_expectations.items():
                field = ProductModel._meta.get_field(field_name)
                self.assertEqual(expected_values[0], str(field.verbose_name))
                self.assertEqual(expected_values[1], str(field.help_text))

            for field_name, expected_values in variant_field_expectations.items():
                field = ProductVariantModel._meta.get_field(field_name)
                self.assertEqual(expected_values[0], str(field.verbose_name))
                self.assertEqual(expected_values[1], str(field.help_text))

            for field_name, expected_values in image_field_expectations.items():
                field = ProductImageModel._meta.get_field(field_name)
                self.assertEqual(expected_values[0], str(field.verbose_name))
                self.assertEqual(expected_values[1], str(field.help_text))

        with override("es"):
            self.assertEqual("Negocio", str(ProductModel._meta.get_field("tenant").verbose_name))
            self.assertEqual(
                "Negocio al que pertenece este producto y los datos relacionados de su catálogo.",
                str(ProductModel._meta.get_field("tenant").help_text),
            )
            self.assertEqual("Imagen principal", str(ProductImageModel._meta.get_field("is_primary").verbose_name))
            self.assertEqual(
                "Usa esta imagen como imagen principal del producto o de la variante.",
                str(ProductImageModel._meta.get_field("is_primary").help_text),
            )
