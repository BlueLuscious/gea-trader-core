from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import override
from core.testing.base import LoggedTestCase
from cart.models import CartModel
from catalog.models import ProductModel, ProductVariantModel
from tenancy.models import TenantModel
from quotation.choices import QuoteWorkflowStatus
from quotation.models import QuoteItemModel, QuoteModel


class TestQuotationModel(LoggedTestCase):
    """ Cover quotation model behavior. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for catalog-linked quotation fixtures.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_quote_and_snapshot_item_relationships(self) -> None:
        """ Verify quote and quote item relationships persist correctly. """
        tenant = self._create_tenant("quotation-model")
        cart = CartModel.objects.create(tenant=tenant, session_key='session-quote')
        product = ProductModel.objects.create(tenant=tenant, name='Bomba', slug='bomba')
        variant = ProductVariantModel.objects.create(product=product, sku='BOM-001')
        quote = QuoteModel.objects.create(tenant=tenant, cart=cart, customer_email='cliente@example.com')
        item = QuoteItemModel.objects.create(
            quote=quote,
            product=product,
            variant=variant,
            product_name_snapshot=product.name,
            sku_snapshot=variant.sku,
            attributes_snapshot=variant.attributes_json,
            quantity=3
        )

        self.assertEqual(quote.tenant, tenant)
        self.assertEqual(item.quote, quote)
        self.assertEqual(item.product, product)
        self.assertEqual(item.variant, variant)

    def test_string_representations_are_admin_friendly(self) -> None:
        """ Verify quote models expose admin-friendly labels. """
        tenant = self._create_tenant("quotation-strings")
        quote = QuoteModel.objects.create(tenant=tenant, customer_email='cliente@example.com')
        item = QuoteItemModel.objects.create(quote=quote, product_name_snapshot='Bomba', quantity=1)

        self.assertEqual(str(quote), f'Quote {quote.pk}')
        self.assertEqual(str(item), 'Bomba')

    def test_quote_item_quantity_must_be_positive(self) -> None:
        """ Verify quote items reject zero quantity at the model layer. """
        tenant = self._create_tenant("quotation-quantity")
        quote = QuoteModel.objects.create(tenant=tenant, customer_email="cliente@example.com")
        item = QuoteItemModel(
            quote=quote,
            product_name_snapshot="Bomba",
            quantity=0,
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_quote_rejects_source_cart_from_another_tenant(self) -> None:
        """ Verify a quote cannot reference a cart that belongs to another tenant. """
        tenant = self._create_tenant("quotation-cart-scope")
        other_tenant = self._create_tenant("quotation-cart-scope-other")
        foreign_cart = CartModel.objects.create(tenant=other_tenant, session_key="foreign-cart")

        with self.assertRaises(ValidationError):
            QuoteModel.objects.create(
                tenant=tenant,
                cart=foreign_cart,
                customer_email="cliente@example.com",
            )

    def test_quote_workflow_timestamps_are_derived_from_internal_progress(self) -> None:
        """ Verify requested and resolved timestamps follow the internal workflow status. """
        tenant = self._create_tenant("quotation-workflow-timestamps")
        draft_quote = QuoteModel.objects.create(tenant=tenant, customer_email="draft@example.com")
        requested_quote = QuoteModel.objects.create(
            tenant=tenant,
            customer_email="requested@example.com",
            workflow_status=QuoteWorkflowStatus.REQUESTED,
        )
        in_progress_quote = QuoteModel.objects.create(
            tenant=tenant,
            customer_email="progress@example.com",
            workflow_status=QuoteWorkflowStatus.IN_PROGRESS,
        )
        completed_quote = QuoteModel.objects.create(
            tenant=tenant,
            customer_email="completed@example.com",
            workflow_status=QuoteWorkflowStatus.COMPLETED,
        )
        cancelled_quote = QuoteModel.objects.create(
            tenant=tenant,
            customer_email="cancelled@example.com",
            workflow_status=QuoteWorkflowStatus.CANCELLED,
        )

        self.assertIsNone(draft_quote.requested_at)
        self.assertIsNone(draft_quote.resolved_at)
        self.assertIsNotNone(requested_quote.requested_at)
        self.assertIsNone(requested_quote.resolved_at)
        self.assertIsNotNone(in_progress_quote.requested_at)
        self.assertIsNone(in_progress_quote.resolved_at)
        self.assertIsNotNone(completed_quote.requested_at)
        self.assertIsNotNone(completed_quote.resolved_at)
        self.assertIsNotNone(cancelled_quote.requested_at)
        self.assertIsNotNone(cancelled_quote.resolved_at)

    def test_quote_workflow_timestamps_are_first_write_only(self) -> None:
        """ Verify derived workflow timestamps stay stable after later updates. """
        tenant = self._create_tenant("quotation-workflow-first-write")
        quote = QuoteModel.objects.create(
            tenant=tenant,
            customer_email="requested@example.com",
            workflow_status=QuoteWorkflowStatus.REQUESTED,
        )
        first_requested_at = quote.requested_at

        quote.workflow_status = QuoteWorkflowStatus.COMPLETED
        quote.save()
        first_resolved_at = quote.resolved_at

        quote.notes = "Updated after closure"
        quote.save()
        quote.refresh_from_db()

        self.assertEqual(first_requested_at, quote.requested_at)
        self.assertEqual(first_resolved_at, quote.resolved_at)

    def test_quote_rejects_backward_workflow_transitions(self) -> None:
        """ Verify workflow transitions cannot move backward once the quote progresses. """
        tenant = self._create_tenant("quotation-workflow-backward")
        quote = QuoteModel.objects.create(
            tenant=tenant,
            customer_email="progress@example.com",
            workflow_status=QuoteWorkflowStatus.IN_PROGRESS,
        )

        quote.workflow_status = QuoteWorkflowStatus.REQUESTED

        with self.assertRaises(ValidationError):
            quote.save()

    def test_quote_rejects_terminal_workflow_switches(self) -> None:
        """ Verify terminal workflow states cannot switch once the quote is resolved internally. """
        tenant = self._create_tenant("quotation-workflow-terminal")
        quote = QuoteModel.objects.create(
            tenant=tenant,
            customer_email="completed@example.com",
            workflow_status=QuoteWorkflowStatus.COMPLETED,
        )

        quote.workflow_status = QuoteWorkflowStatus.CANCELLED

        with self.assertRaises(ValidationError):
            quote.save()

    def test_model_field_metadata_uses_friendly_translatable_copy(self) -> None:
        """ Verify quotation model fields expose user-friendly labels and help texts. """
        quote_field_expectations = {
            "tenant": ("Business", "Business that owns this quote and the follow-up around it."),
            "user": ("Customer account", "Optional customer account related to this quote."),
            "workflow_status": ("Workflow status", "Current internal workflow stage of this quote."),
            "notes": ("Internal notes", "Private notes not intended for customers."),
            "resolved_at": ("Resolved at", "When the internal workflow for this quote reached a terminal resolution."),
        }
        item_field_expectations = {
            "quote": ("Quote", "Quote this line item belongs to."),
            "product_name_snapshot": ("Product name snapshot", "Product name captured when this quote item was created."),
            "unit_price_snapshot": ("Unit price snapshot", "Unit price captured when this quote item was created."),
        }

        with override("en"):
            app_config = apps.get_app_config("quotation")

            self.assertEqual("Quotations", str(app_config.verbose_name))

            for field_name, expected_values in quote_field_expectations.items():
                field = QuoteModel._meta.get_field(field_name)
                self.assertEqual(expected_values[0], str(field.verbose_name))
                self.assertEqual(expected_values[1], str(field.help_text))

            for field_name, expected_values in item_field_expectations.items():
                field = QuoteItemModel._meta.get_field(field_name)
                self.assertEqual(expected_values[0], str(field.verbose_name))
                self.assertEqual(expected_values[1], str(field.help_text))
