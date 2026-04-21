""" Single-tenant public home view tests for the front app. """

from core.testing.base import LoggedTestCase
from catalog.models import ProductModel, ProductVariantModel
from masterdata.models import CategoryModel
from tenancy.models import TenantBrandingModel, TenantModel


class TestFrontViews(LoggedTestCase):
    """ Verify the current public home route and its single-tenant context. """

    def setUp(self) -> None:
        """ Create one active public tenant with featured products and categories for the home hero. """
        self.tenant = TenantModel.objects.create(
            name="GEA Oils",
            slug="gea-oils",
            business_email="info@geaoils.test",
            phone_number="+54 11 1234 5678",
            is_active=True,
        )
        TenantBrandingModel.objects.create(
            tenant=self.tenant,
            display_name="GEA Trader",
            favicon_light="branding/favicons/gea-light.ico",
            favicon_dark="branding/favicons/gea-dark.ico",
            instagram_url="https://instagram.com/gea.trader",
            facebook_url="https://facebook.com/geatrader",
            linkedin_url="https://linkedin.com/company/gea-trader",
        )
        self.lubricants_category = CategoryModel.objects.create(
            tenant=self.tenant,
            name="Lubricants",
            slug="lubricants",
            is_active=True,
            is_featured=True,
        )
        CategoryModel.objects.create(
            tenant=self.tenant,
            name="Greases",
            slug="greases",
            is_active=True,
            is_featured=True,
        )
        self.hydraulic_subcategory = CategoryModel.objects.create(
            tenant=self.tenant,
            name="Hydraulic Oils",
            slug="hydraulic-oils",
            parent=self.lubricants_category,
            is_active=True,
        )

        self.featured_product = ProductModel.objects.create(
            tenant=self.tenant,
            category=self.lubricants_category,
            name="Premium Lubricant",
            slug="premium-lubricant",
            is_active=True,
            is_featured=True,
            requires_quote=True,
        )
        ProductVariantModel.objects.create(
            product=self.featured_product,
            name="20L Drum",
            sku="PREMIUM-20L",
            is_default=True,
            is_active=True,
        )
        ProductVariantModel.objects.create(
            product=self.featured_product,
            name="205L Drum",
            sku="PREMIUM-205L",
            is_default=False,
            is_active=True,
            price="125000.00",
        )
        self.subcategory_product = ProductModel.objects.create(
            tenant=self.tenant,
            category=self.hydraulic_subcategory,
            name="Hydraulic Oil 46",
            slug="hydraulic-oil-46",
            is_active=True,
            requires_quote=False,
        )
        ProductVariantModel.objects.create(
            product=self.subcategory_product,
            name="205L Drum",
            sku="HYD-46-205L",
            is_default=True,
            is_active=True,
            price="98000.00",
        )

    def test_index_renders_the_public_home_hero(self) -> None:
        """ Verify the public root renders the current public-home shell. """
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["site_brand_name"], "GEA Trader")
        self.assertEqual(len(response.context["featured_products"]), 1)
        self.assertContains(response, "GEA Trader")
        self.assertContains(response, "En Gea Trader trabajamos junto a vos para que las cosas pasen")
        self.assertContains(response, "Productos destacados")
        self.assertContains(response, "Productos nuevos")
        self.assertContains(response, "Categorías")
        self.assertContains(response, self.featured_product.name)
        self.assertContains(response, f"/productos/{self.featured_product.slug}/")
        self.assertContains(response, "/productos/")
        self.assertContains(response, "/categorias/")
        self.assertContains(response, f"/categorias/{self.lubricants_category.slug}/")
        self.assertContains(response, "mailto:info@geaoils.test")
        self.assertContains(response, "+54 11 1234 5678")
        self.assertContains(response, "https://wa.me/541112345678")
        self.assertContains(response, "https://instagram.com/gea.trader")
        self.assertContains(response, "https://facebook.com/geatrader")
        self.assertContains(response, "https://linkedin.com/company/gea-trader")
        self.assertContains(response, '/media/branding/favicons/gea-light.ico')
        self.assertContains(response, '/media/branding/favicons/gea-dark.ico')

    def test_public_home_returns_not_found_when_no_active_tenant_exists(self) -> None:
        """ Verify the public root returns not found when no active tenant is available. """
        self.tenant.is_active = False
        self.tenant.save(update_fields=["is_active"])

        response = self.client.get("/")

        self.assertEqual(response.status_code, 404)

    def test_product_detail_renders_active_variants(self) -> None:
        """ Verify one product detail page renders product data and active variants. """
        response = self.client.get(f"/productos/{self.featured_product.slug}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.featured_product.name)
        self.assertContains(response, "Variantes disponibles")
        self.assertContains(response, "20L Drum")
        self.assertContains(response, "205L Drum")
        self.assertContains(response, "SKU: PREMIUM-20L")

    def test_product_detail_returns_not_found_for_unknown_slug(self) -> None:
        """ Verify unknown product slugs return not found in the public site. """
        response = self.client.get("/productos/no-existe/")

        self.assertEqual(response.status_code, 404)

    def test_product_list_renders_active_products(self) -> None:
        """ Verify the public product catalog renders active products. """
        response = self.client.get("/productos/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Productos")
        self.assertContains(response, "2 productos activos")
        self.assertContains(response, self.featured_product.name)
        self.assertContains(response, self.subcategory_product.name)

    def test_category_list_renders_root_categories_and_active_children(self) -> None:
        """ Verify the public category index renders root categories and child shortcuts. """
        response = self.client.get("/categorias/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Categorías")
        self.assertContains(response, self.lubricants_category.name)
        self.assertContains(response, "Greases")
        self.assertContains(response, self.hydraulic_subcategory.name)
        self.assertContains(response, f"/categorias/{self.lubricants_category.slug}/")

    def test_category_list_paginates_root_categories_twelve_per_page(self) -> None:
        """ Verify the public category index paginates root categories with twelve groups per page. """
        for index in range(13):
            CategoryModel.objects.create(
                tenant=self.tenant,
                name=f"Root Category {index:02d}",
                slug=f"root-category-{index:02d}",
                is_active=True,
            )

        first_page_response = self.client.get("/categorias/")
        second_page_response = self.client.get("/categorias/", {"page": 2})

        self.assertEqual(first_page_response.status_code, 200)
        self.assertEqual(second_page_response.status_code, 200)
        self.assertContains(first_page_response, "Root Category 00")
        self.assertContains(first_page_response, "Root Category 09")
        self.assertNotContains(first_page_response, "Root Category 12")
        self.assertContains(second_page_response, "Root Category 12")

    def test_category_page_lists_products_from_root_and_direct_subcategories(self) -> None:
        """ Verify one category page renders products from the root category and its direct children. """
        response = self.client.get(f"/categorias/{self.lubricants_category.slug}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lubricants_category.name)
        self.assertContains(response, self.featured_product.name)
        self.assertContains(response, self.subcategory_product.name)
        self.assertContains(response, self.hydraulic_subcategory.name)

    def test_category_page_filters_products_by_selected_subcategory(self) -> None:
        """ Verify the category page narrows the grid when one subcategory filter is selected. """
        response = self.client.get(
            f"/categorias/{self.lubricants_category.slug}/",
            {"subcategoria": self.hydraulic_subcategory.slug},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.subcategory_product.name)
        self.assertNotContains(response, self.featured_product.name)

    def test_category_page_paginates_products_twelve_per_page(self) -> None:
        """ Verify the category page paginates product cards with twelve products per page. """
        for index in range(13):
            product = ProductModel.objects.create(
                tenant=self.tenant,
                category=self.lubricants_category,
                name=f"Catalog Product {index:02d}",
                slug=f"catalog-product-{index:02d}",
                is_active=True,
                requires_quote=False,
            )
            ProductVariantModel.objects.create(
                product=product,
                name="Base",
                sku=f"CAT-{index}",
                is_default=True,
                is_active=True,
                price="1000.00",
            )

        first_page_response = self.client.get(f"/categorias/{self.lubricants_category.slug}/")
        second_page_response = self.client.get(f"/categorias/{self.lubricants_category.slug}/", {"page": 2})

        self.assertEqual(first_page_response.status_code, 200)
        self.assertEqual(second_page_response.status_code, 200)
        self.assertContains(first_page_response, "Catalog Product 00")
        self.assertContains(first_page_response, "Catalog Product 09")
        self.assertNotContains(first_page_response, "Catalog Product 12")
        self.assertContains(second_page_response, "Catalog Product 12")

    def test_product_list_paginates_products_twelve_per_page(self) -> None:
        """ Verify the public product catalog paginates product cards with twelve products per page. """
        for index in range(13):
            product = ProductModel.objects.create(
                tenant=self.tenant,
                category=self.lubricants_category,
                name=f"Store Product {index:02d}",
                slug=f"store-product-{index:02d}",
                is_active=True,
                requires_quote=False,
            )
            ProductVariantModel.objects.create(
                product=product,
                name="Base",
                sku=f"STORE-{index}",
                is_default=True,
                is_active=True,
                price="1000.00",
            )

        first_page_response = self.client.get("/productos/")
        second_page_response = self.client.get("/productos/", {"page": 2})

        self.assertEqual(first_page_response.status_code, 200)
        self.assertEqual(second_page_response.status_code, 200)
        self.assertContains(first_page_response, "Store Product 00")
        self.assertContains(first_page_response, "Store Product 09")
        self.assertNotContains(first_page_response, "Store Product 12")
        self.assertContains(second_page_response, "Store Product 12")
