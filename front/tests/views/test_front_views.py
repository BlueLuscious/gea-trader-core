from django.core import mail
from django.test import override_settings
from django.utils import timezone

from core.testing.base import LoggedTestCase
from cart.choices import CartStatus
from cart.models import CartItemModel, CartModel
from cart.settings import CART_RUNTIME_EXPIRATION_HOURS
from catalog.models import ProductModel, ProductVariantModel
from masterdata.models import CategoryModel
from quotation.models import QuoteItemModel, QuoteModel
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
        self.assertContains(response, "/media/branding/favicons/gea-light.ico")
        self.assertContains(response, "/media/branding/favicons/gea-dark.ico")

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
        self.assertContains(response, "2 productos")
        self.assertContains(response, self.featured_product.name)
        self.assertContains(response, self.subcategory_product.name)
        self.assertContains(response, 'class="site-footer"')
        self.assertContains(response, "mailto:info@geaoils.test")

    def test_category_list_renders_root_categories_and_active_children(self) -> None:
        """ Verify the public category index renders root categories and child shortcuts. """
        response = self.client.get("/categorias/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Categorías")
        self.assertContains(response, self.lubricants_category.name)
        self.assertContains(response, "Greases")
        self.assertContains(response, self.hydraulic_subcategory.name)
        self.assertContains(response, f"/categorias/{self.lubricants_category.slug}/")
        self.assertContains(
            response,
            f"/categorias/{self.lubricants_category.slug}/?subcategoria={self.hydraulic_subcategory.slug}",
        )
        self.assertNotContains(response, f"/categorias/{self.hydraulic_subcategory.slug}/")

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

    def test_category_page_returns_not_found_for_direct_subcategory_slug(self) -> None:
        """ Verify public category pages only resolve root-category slugs directly. """
        response = self.client.get(f"/categorias/{self.hydraulic_subcategory.slug}/")

        self.assertEqual(response.status_code, 404)

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

    def test_product_list_paginates_products_twenty_four_per_page(self) -> None:
        """ Verify the public product catalog paginates product cards with twenty-four products per page. """
        for index in range(25):
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
        self.assertContains(first_page_response, "Store Product 21")
        self.assertNotContains(first_page_response, "Store Product 22")
        self.assertContains(second_page_response, "Store Product 22")

    def test_cart_state_returns_empty_payload_when_no_cart_exists(self) -> None:
        """ Verify the public cart state endpoint returns one empty runtime payload by default. """
        response = self.client.get("/carrito/estado/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["cart_id"], None)
        self.assertEqual(payload["status"], "")
        self.assertEqual(payload["items"], [])
        self.assertEqual(payload["count"], 0)
        self.assertEqual(payload["items_html"], "")
        self.assertEqual(payload["summary_html"], "")

    def test_cart_add_item_creates_one_persisted_active_cart(self) -> None:
        """ Verify adding one product creates one persisted active cart scoped to the current tenant. """
        response = self.client.post(
            "/carrito/agregar/",
            data='{"product_id": %s, "quantity": 1}' % self.subcategory_product.id,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CartModel.objects.count(), 1)
        self.assertEqual(CartItemModel.objects.count(), 1)
        cart = CartModel.objects.get()
        cart_item = CartItemModel.objects.get()
        self.assertEqual(cart.tenant, self.tenant)
        self.assertIsNotNone(cart.expires_at)
        self.assertGreater(cart.expires_at, timezone.now() + timezone.timedelta(hours=CART_RUNTIME_EXPIRATION_HOURS - 1))
        self.assertLessEqual(
            cart.expires_at,
            timezone.now() + timezone.timedelta(hours=CART_RUNTIME_EXPIRATION_HOURS, seconds=5),
        )
        self.assertEqual(cart_item.product, self.subcategory_product)
        self.assertEqual(cart_item.variant.sku, "HYD-46-205L")
        payload = response.json()
        self.assertEqual(payload["cart_id"], cart.id)
        self.assertEqual(payload["status"], "active")
        self.assertEqual(payload["count"], 1)
        self.assertEqual(len(payload["items"]), 1)
        self.assertEqual(payload["items"][0]["id"], cart_item.id)
        self.assertEqual(payload["items"][0]["product_id"], self.subcategory_product.id)
        self.assertEqual(payload["items"][0]["variant_id"], cart_item.variant_id)
        self.assertEqual(payload["items"][0]["title"], "Hydraulic Oil 46")
        self.assertEqual(payload["items"][0]["subtitle"], "205L Drum")
        self.assertEqual(payload["items"][0]["sku"], "HYD-46-205L")
        self.assertEqual(payload["items"][0]["price"], "98000.00")
        self.assertEqual(payload["items"][0]["price_text"], "ARS 98000.00")
        self.assertIn("Hydraulic Oil 46", payload["items_html"])
        self.assertIn("HYD-46-205L", payload["items_html"])
        self.assertNotIn("Subtotal estimado", payload["summary_html"])

    def test_cart_add_item_uses_product_base_sku_when_variant_sku_is_empty(self) -> None:
        """ Verify cart runtime payloads expose the effective variant SKU. """
        product = ProductModel.objects.create(
            tenant=self.tenant,
            category=self.lubricants_category,
            name="Fallback SKU Oil",
            slug="fallback-sku-oil",
            sku_base="FALLBACK-SKU",
            is_active=True,
        )
        ProductVariantModel.objects.create(
            product=product,
            name="Base package",
            sku="",
            is_default=True,
            is_active=True,
        )

        response = self.client.post(
            "/carrito/agregar/",
            data='{"product_id": %s, "quantity": 1}' % product.id,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["items"][0]["sku"], "FALLBACK-SKU")
        self.assertIn("FALLBACK-SKU", payload["items_html"])

    def test_cart_state_ignores_abandoned_cart_for_the_current_session(self) -> None:
        """ Verify abandoned carts are not exposed as the current public cart state. """
        self.client.post(
            "/carrito/agregar/",
            data='{"product_id": %s, "quantity": 1}' % self.subcategory_product.id,
            content_type="application/json",
        )
        cart = CartModel.objects.get()
        cart.status = CartStatus.ABANDONED
        cart.save(update_fields=["status", "updated_at"])

        response = self.client.get("/carrito/estado/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsNone(payload["cart_id"])
        self.assertEqual("", payload["status"])
        self.assertEqual([], payload["items"])
        self.assertEqual(0, payload["count"])

    def test_cart_add_item_creates_new_cart_when_previous_session_cart_is_abandoned(self) -> None:
        """ Verify adding after expiration does not reuse an abandoned cart. """
        first_response = self.client.post(
            "/carrito/agregar/",
            data='{"product_id": %s, "quantity": 1}' % self.subcategory_product.id,
            content_type="application/json",
        )
        first_cart = CartModel.objects.get(id=first_response.json()["cart_id"])
        first_cart.status = CartStatus.ABANDONED
        first_cart.save(update_fields=["status", "updated_at"])

        second_response = self.client.post(
            "/carrito/agregar/",
            data='{"product_id": %s, "quantity": 1}' % self.subcategory_product.id,
            content_type="application/json",
        )

        self.assertEqual(second_response.status_code, 200)
        payload = second_response.json()
        self.assertNotEqual(first_cart.id, payload["cart_id"])
        self.assertEqual("active", payload["status"])
        self.assertEqual(2, CartModel.objects.count())
        self.assertEqual(1, CartModel.objects.active().count())
        self.assertEqual(1, CartModel.objects.abandoned().count())

    def test_cart_update_quantity_keeps_one_line_item_in_the_public_count(self) -> None:
        """ Verify quantity changes do not inflate the public cart count beyond one line item. """
        self.client.post(
            "/carrito/agregar/",
            data='{"product_id": %s, "quantity": 1}' % self.subcategory_product.id,
            content_type="application/json",
        )
        cart_item = CartItemModel.objects.get()

        response = self.client.post(
            "/carrito/cantidad/",
            data='{"item_id": %s, "quantity": 3}' % cart_item.id,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)
        payload = response.json()
        self.assertEqual(payload["count"], 1)

    def test_cart_remove_item_deletes_one_persisted_line(self) -> None:
        """ Verify the public cart can remove one persisted item and return an empty cart state. """
        self.client.post(
            "/carrito/agregar/",
            data='{"product_id": %s, "quantity": 1}' % self.subcategory_product.id,
            content_type="application/json",
        )
        cart_item = CartItemModel.objects.get()

        response = self.client.post(
            "/carrito/quitar/",
            data='{"item_id": %s}' % cart_item.id,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CartItemModel.objects.count(), 0)
        self.assertContains(response, '"items": []')
        self.assertContains(response, '"count": 0')

    def test_base_layout_pre_renders_quote_request_form_inside_the_modal(self) -> None:
        """ Verify the shared public layout includes the initial quote-request form markup. """
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-quote-request-modal-content')
        self.assertContains(response, "Solicitar cotización")
        self.assertContains(response, "Nombre y apellido")
        self.assertContains(response, 'data-cart-quote-form')

    def test_cart_quote_request_get_returns_the_rendered_form(self) -> None:
        """ Verify the public cart quote endpoint returns the rendered request form. """
        self.client.post(
            "/carrito/agregar/",
            data='{"product_id": %s, "quantity": 1}' % self.subcategory_product.id,
            content_type="application/json",
        )

        response = self.client.get("/carrito/cotizar/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertIn("Solicitar cotización", payload["form_html"])
        self.assertIn("Nombre y apellido", payload["form_html"])
        self.assertIn('data-modal-close-target="site-quote-request-modal"', payload["form_html"])

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_cart_quote_request_post_creates_quote_items_and_notifies_tenant(self) -> None:
        """ Verify the public cart quote endpoint creates one quote, snapshots items, and sends notification mail. """
        self.client.post(
            "/carrito/agregar/",
            data='{"product_id": %s, "quantity": 2}' % self.subcategory_product.id,
            content_type="application/json",
        )

        response = self.client.post(
            "/carrito/cotizar/",
            data={
                "customer_name": "Ada Lovelace",
                "customer_email": "ada@example.com",
                "customer_phone": "+54 11 5555 0000",
                "company_name": "Analytical Engines",
                "message": "Necesito disponibilidad y plazo de entrega.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuoteModel.objects.count(), 1)
        self.assertEqual(QuoteItemModel.objects.count(), 1)
        quote = QuoteModel.objects.get()
        quote_item = QuoteItemModel.objects.get()
        cart = CartModel.objects.get()
        self.assertEqual(quote.tenant, self.tenant)
        self.assertEqual(quote.cart, cart)
        self.assertEqual(quote.workflow_status, "requested")
        self.assertEqual(quote.customer_name, "Ada Lovelace")
        self.assertEqual(quote.customer_email, "ada@example.com")
        self.assertEqual(quote.customer_phone, "+54 11 5555 0000")
        self.assertEqual(quote.company_name, "Analytical Engines")
        self.assertEqual(quote.notes, "Necesito disponibilidad y plazo de entrega.")
        self.assertEqual(quote_item.product_name_snapshot, "Hydraulic Oil 46")
        self.assertEqual(quote_item.sku_snapshot, "HYD-46-205L")
        self.assertEqual(quote_item.quantity, 2)
        self.assertEqual(str(quote_item.unit_price_snapshot), "98000.00")
        self.assertEqual(cart.status, "converted")
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["quote_id"], quote.id)
        self.assertIn("Gracias, Ada Lovelace", payload["message"])
        self.assertEqual(payload["cart_state"]["count"], 0)
        self.assertTrue(quote.id)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Ada Lovelace", mail.outbox[0].subject)
        self.assertIn("Hydraulic Oil 46", mail.outbox[0].body)
