from django.core.files.uploadedfile import SimpleUploadedFile
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

    def test_product_slug_can_repeat_across_different_tenants(self) -> None:
        """ Allow the same product slug when each tenant owns a separate catalog. """
        first_tenant = self._create_tenant("north")
        second_tenant = self._create_tenant("south")

        first_product = ProductModel.objects.create(tenant=first_tenant, name="Bomba", slug="bomba")
        second_product = ProductModel.objects.create(tenant=second_tenant, name="Bomba", slug="bomba")

        self.assertEqual(first_product.slug, second_product.slug)

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
