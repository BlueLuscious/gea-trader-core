""" Owner admin tests for tenant-scoped quotation flows. """

from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth.models import Permission
from django.test import RequestFactory
from django.utils.translation import override
from unfold.fields import UnfoldAdminReadonlyField
from accounts.models import UserModel
from catalog.models import ProductModel, ProductVariantModel
from core.adminsites.site_instances import owner_admin_site
from core.testing.base import LoggedTestCase
from quotation.choices import QuoteWorkflowStatus
from quotation.admin.owner.quote_item_model_inline import QuoteItemModelInline
from quotation.admin.owner.quote_model_admin import QuoteModelAdmin
from quotation.models import QuoteItemModel, QuoteModel
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestOwnerQuotationAdmin(LoggedTestCase):
    """ Verify the owner quotation admin stays scoped to the active tenant. """

    def setUp(self) -> None:
        """ Create reusable request factory, tenant, operator, and quote fixtures. """
        self.request_factory = RequestFactory()
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        self.operator = UserModel.objects.create_user(
            username="quotation-operator",
            password="test-pass",
            is_active=True,
            is_staff=True,
        )
        self.outsider = UserModel.objects.create_user(
            username="quotation-outsider",
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
                codename__in=("view_quotemodel", "add_quotemodel", "change_quotemodel")
            )
        )
        self.in_scope_quote = QuoteModel.objects.create(
            tenant=self.tenant,
            customer_email="north@example.com",
        )
        self.out_of_scope_quote = QuoteModel.objects.create(
            tenant=self.other_tenant,
            customer_email="south@example.com",
        )
        self.in_scope_product = ProductModel.objects.create(
            tenant=self.tenant,
            name="Pump",
            slug="pump",
            sku_base="PUMP",
        )
        self.out_of_scope_product = ProductModel.objects.create(
            tenant=self.other_tenant,
            name="Filter",
            slug="filter",
            sku_base="FILTER",
        )
        self.in_scope_variant = ProductVariantModel.objects.create(
            product=self.in_scope_product,
            sku="PUMP-001",
            price=Decimal("42.50"),
            is_default=True,
        )
        ProductVariantModel.objects.create(
            product=self.out_of_scope_product,
            sku="FILTER-001",
        )
        self.admin = QuoteModelAdmin(QuoteModel, owner_admin_site)

    def build_request(self, user: UserModel, tenant: TenantModel | None) -> object:
        """ Build one owner-admin request for one user and tenant context.

        Args:
            user: Authenticated actor.
            tenant: Active tenant in scope.

        Returns:
            object: Request object carrying the actor and tenant.
        """
        request = self.request_factory.get("/owner-admin/quotation/quotemodel/")
        request.user = user
        request.tenant = tenant
        return request

    def test_get_queryset_is_scoped_to_the_active_tenant(self) -> None:
        """ Verify the owner quote queryset only returns quotes from the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        with patch("quotation.admin.owner.quote_model_admin.logger.info") as logger_info_mock:
            queryset = self.admin.get_queryset(request)

        self.assertEqual([self.in_scope_quote], list(queryset))
        logger_info_mock.assert_called_once()

    def test_save_model_assigns_the_active_tenant_on_create(self) -> None:
        """ Verify owner-created quotes inherit the active tenant automatically. """
        request = self.build_request(self.operator, self.tenant)
        quote = QuoteModel(customer_name="Manual quote", customer_email="manual@example.com")
        form = QuoteModelAdmin.form(instance=quote)

        with patch("quotation.admin.owner.quote_model_admin.logger.info") as logger_info_mock:
            self.admin.save_model(request, quote, form, change=False)

        self.assertEqual(self.tenant, quote.tenant)
        logger_info_mock.assert_any_call(
            "Saved owner quote tenant_id=%s quote_id=%s change=%s",
            self.tenant.pk,
            quote.pk,
            False,
        )

    def test_view_and_change_permissions_reject_quotes_from_other_tenants(self) -> None:
        """ Verify quote object permissions stay scoped to the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(self.admin.has_view_permission(request, self.in_scope_quote))
        self.assertTrue(self.admin.has_change_permission(request, self.in_scope_quote))
        self.assertFalse(self.admin.has_view_permission(request, self.out_of_scope_quote))
        self.assertFalse(self.admin.has_change_permission(request, self.out_of_scope_quote))

    def test_module_and_add_permissions_require_quotation_access(self) -> None:
        """ Verify quotation module and add access stay blocked without tenant membership. """
        member_request = self.build_request(self.operator, self.tenant)
        outsider_request = self.build_request(self.outsider, self.tenant)

        self.assertTrue(self.admin.has_module_permission(member_request))
        self.assertTrue(self.admin.has_add_permission(member_request))
        self.assertFalse(self.admin.has_module_permission(outsider_request))
        self.assertFalse(self.admin.has_add_permission(outsider_request))

    def test_bulk_workflow_actions_require_change_permission(self) -> None:
        """ Verify view-only operators cannot access bulk quote workflow actions. """
        request = self.build_request(self.operator, self.tenant)
        self.operator.user_permissions.remove(
            Permission.objects.get(codename="change_quotemodel", content_type__app_label="quotation")
        )
        self.operator = UserModel.objects.get(pk=self.operator.pk)
        request.user = self.operator

        available_actions = self.admin.get_actions(request)

        self.assertFalse(self.admin.has_change_permission(request))
        self.assertNotIn("complete_selected_quotes", available_actions)
        self.assertNotIn("cancel_selected_quotes", available_actions)

    def test_submit_line_actions_are_available_only_for_open_quotes(self) -> None:
        """ Verify owner quote submit-line actions disappear after terminal resolution. """
        request = self.build_request(self.operator, self.tenant)
        open_actions = self.admin.get_actions_submit_line(request, self.in_scope_quote.pk)
        self.in_scope_quote.workflow_status = QuoteWorkflowStatus.COMPLETED
        self.in_scope_quote.save()

        terminal_actions = self.admin.get_actions_submit_line(request, self.in_scope_quote.pk)

        self.assertEqual(
            ["quotation_quotemodel_complete_quote", "quotation_quotemodel_cancel_quote"],
            [action.action_name for action in open_actions],
        )
        self.assertEqual([], terminal_actions)

    def test_submit_line_complete_action_marks_one_quote_completed(self) -> None:
        """ Verify the owner change-form complete button uses the workflow service path. """
        request = self.build_request(self.operator, self.tenant)

        with patch.object(self.admin, "message_user") as message_user_mock:
            self.admin.complete_quote(request, self.in_scope_quote)

        self.in_scope_quote.refresh_from_db()

        self.assertEqual(QuoteWorkflowStatus.COMPLETED, self.in_scope_quote.workflow_status)
        self.assertIsNotNone(self.in_scope_quote.resolved_at)
        message_user_mock.assert_called_once()

    def test_submit_line_cancel_action_marks_one_quote_cancelled(self) -> None:
        """ Verify the owner change-form cancel button uses the workflow service path. """
        request = self.build_request(self.operator, self.tenant)

        with patch.object(self.admin, "message_user") as message_user_mock:
            self.admin.cancel_quote(request, self.in_scope_quote)

        self.in_scope_quote.refresh_from_db()

        self.assertEqual(QuoteWorkflowStatus.CANCELLED, self.in_scope_quote.workflow_status)
        self.assertIsNotNone(self.in_scope_quote.resolved_at)
        message_user_mock.assert_called_once()

    def test_changelist_complete_action_marks_selected_quotes_completed(self) -> None:
        """ Verify the bulk complete admin action transitions selected quotes. """
        request = self.build_request(self.operator, self.tenant)

        with patch.object(self.admin, "message_user") as message_user_mock:
            self.admin.complete_selected_quotes(
                request,
                QuoteModel.objects.filter(pk=self.in_scope_quote.pk),
            )

        self.in_scope_quote.refresh_from_db()

        self.assertEqual(QuoteWorkflowStatus.COMPLETED, self.in_scope_quote.workflow_status)
        message_user_mock.assert_called_once()

    def test_changelist_cancel_action_marks_selected_quotes_cancelled(self) -> None:
        """ Verify the bulk cancel admin action transitions selected quotes. """
        request = self.build_request(self.operator, self.tenant)

        with patch.object(self.admin, "message_user") as message_user_mock:
            self.admin.cancel_selected_quotes(
                request,
                QuoteModel.objects.filter(pk=self.in_scope_quote.pk),
            )

        self.in_scope_quote.refresh_from_db()

        self.assertEqual(QuoteWorkflowStatus.CANCELLED, self.in_scope_quote.workflow_status)
        message_user_mock.assert_called_once()

    def test_quote_item_inline_limits_catalog_choices_to_the_active_tenant(self) -> None:
        """ Verify add-time quote item choices expose only products and variants from the active tenant. """
        with override("en"):
            inline = QuoteItemModelInline(QuoteModel, owner_admin_site)
            request = self.build_request(self.operator, self.tenant)
            request.method = "POST"
            formset_class = inline.get_formset(request, obj=None)
            formset = formset_class(instance=QuoteModel(tenant=self.tenant))
            empty_form = formset.empty_form

            self.assertEqual([self.in_scope_product], list(empty_form.fields["product"].queryset))
            self.assertEqual([self.in_scope_variant], list(empty_form.fields["variant"].queryset))
            self.assertEqual(
                "Optional. If left empty, the default variant for the selected product will be used.",
                empty_form.fields["variant"].help_text,
            )

    def test_quote_item_inline_logs_snapshot_creation_for_the_active_tenant(self) -> None:
        """ Verify add-time quote item snapshot creation logs the current tenant and catalog selection. """
        inline = QuoteItemModelInline(QuoteModel, owner_admin_site)
        request = self.request_factory.post("/owner-admin/quotation/quotemodel/add/")
        request.user = self.operator
        request.tenant = self.tenant
        formset_class = inline.get_formset(request, obj=None)
        prefix = "items"
        formset = formset_class(
            data={
                f"{prefix}-TOTAL_FORMS": "1",
                f"{prefix}-INITIAL_FORMS": "0",
                f"{prefix}-MIN_NUM_FORMS": "0",
                f"{prefix}-MAX_NUM_FORMS": "1000",
                f"{prefix}-0-product": str(self.in_scope_product.pk),
                f"{prefix}-0-variant": str(self.in_scope_variant.pk),
                f"{prefix}-0-quantity": "2",
                f"{prefix}-0-notes": "Urgent",
            },
            instance=QuoteModel(tenant=self.tenant, customer_name="Manual"),
            prefix=prefix,
        )

        self.assertTrue(formset.is_valid(), formset.errors)
        with patch("quotation.admin.owner.quote_item_model_inline_formset.logger.info") as logger_info_mock:
            formset.save(commit=False)

        logger_info_mock.assert_called_once()

    def test_quote_item_inline_renders_attributes_snapshot_through_readonly_key_value_widget(self) -> None:
        """ Verify persisted quote item attributes render through Unfold readonly widget delegation. """
        inline = QuoteItemModelInline(QuoteModel, owner_admin_site)
        QuoteItemModel.objects.create(
            quote=self.in_scope_quote,
            product=self.in_scope_product,
            variant=self.in_scope_variant,
            product_name_snapshot="Pump",
            sku_snapshot="PUMP-001",
            attributes_snapshot={"capacity": "20L"},
            quantity=1,
        )
        request = self.build_request(self.operator, self.tenant)

        fields = inline.get_fields(request, obj=self.in_scope_quote)
        formset_class = inline.get_formset(request, obj=self.in_scope_quote)
        formset = formset_class(instance=self.in_scope_quote)
        form = formset.forms[0]
        readonly_field = UnfoldAdminReadonlyField(
            form,
            "attributes_snapshot",
            is_first=False,
            model_admin=inline,
        )
        rendered_attributes = readonly_field.contents()

        self.assertIn("attributes_snapshot", fields)
        self.assertIn("attributes_snapshot", inline.get_readonly_fields(request, obj=self.in_scope_quote))
        self.assertTrue(form.fields["attributes_snapshot"].disabled)
        self.assertTrue(form.fields["attributes_snapshot"].widget.read_only)
        self.assertIn("capacity", rendered_attributes)
        self.assertIn("20L", rendered_attributes)
        self.assertIn("core-json-key-value", rendered_attributes)
        self.assertIn("core-json-key-value--readonly", rendered_attributes)
        self.assertIn("core-json-key-value__display", rendered_attributes)
        self.assertNotIn('name="items-0-attributes_snapshot__key"', rendered_attributes)
        self.assertNotIn('name="items-0-attributes_snapshot__value"', rendered_attributes)
        self.assertIn("core/forms/widgets/json_key_value_widget.css", str(form.media))

    def test_quote_item_inline_renders_empty_attributes_snapshot_with_dash_placeholders(self) -> None:
        """ Verify empty quote item attributes render as locked key-value dash placeholders. """
        inline = QuoteItemModelInline(QuoteModel, owner_admin_site)
        QuoteItemModel.objects.create(
            quote=self.in_scope_quote,
            product=self.in_scope_product,
            variant=self.in_scope_variant,
            product_name_snapshot="Pump",
            sku_snapshot="PUMP-001",
            attributes_snapshot={},
            quantity=1,
        )
        request = self.build_request(self.operator, self.tenant)

        formset_class = inline.get_formset(request, obj=self.in_scope_quote)
        formset = formset_class(instance=self.in_scope_quote)
        form = formset.forms[0]
        readonly_field = UnfoldAdminReadonlyField(
            form,
            "attributes_snapshot",
            is_first=False,
            model_admin=inline,
        )
        rendered_attributes = readonly_field.contents()

        self.assertEqual(rendered_attributes.count("core-json-key-value__display"), 2)
        self.assertIn("-", rendered_attributes)
        self.assertIn("core-json-key-value--readonly", rendered_attributes)
        self.assertIn("core-json-key-value__display", rendered_attributes)
        self.assertNotIn('name="items-0-attributes_snapshot__key"', rendered_attributes)
        self.assertNotIn('name="items-0-attributes_snapshot__value"', rendered_attributes)

    def test_quote_item_inline_uses_the_default_variant_when_none_is_selected(self) -> None:
        """ Verify quote items fall back to the product default variant when the inline leaves variant empty. """
        inline = QuoteItemModelInline(QuoteModel, owner_admin_site)
        request = self.request_factory.post("/owner-admin/quotation/quotemodel/add/")
        request.user = self.operator
        request.tenant = self.tenant
        formset_class = inline.get_formset(request, obj=None)
        prefix = "items"
        formset = formset_class(
            data={
                f"{prefix}-TOTAL_FORMS": "1",
                f"{prefix}-INITIAL_FORMS": "0",
                f"{prefix}-MIN_NUM_FORMS": "0",
                f"{prefix}-MAX_NUM_FORMS": "1000",
                f"{prefix}-0-product": str(self.in_scope_product.pk),
                f"{prefix}-0-variant": "",
                f"{prefix}-0-quantity": "2",
                f"{prefix}-0-notes": "Urgent",
            },
            instance=QuoteModel(tenant=self.tenant, customer_name="Manual"),
            prefix=prefix,
        )

        self.assertTrue(formset.is_valid(), formset.errors)
        built_items = formset.save(commit=False)
        built_item = built_items[0]

        self.assertEqual(self.in_scope_product, built_item.product)
        self.assertEqual(self.in_scope_variant, built_item.variant)
        self.assertEqual(self.in_scope_variant.sku, built_item.sku_snapshot)
        self.assertEqual(self.in_scope_variant.price, built_item.unit_price_snapshot)
        self.assertEqual({}, built_item.attributes_snapshot)

    def test_quote_item_inline_requires_variant_resolution_when_the_product_has_no_default(self) -> None:
        """ Verify quote items stay invalid when no explicit or default variant can be resolved. """
        with override("en"):
            inline = QuoteItemModelInline(QuoteModel, owner_admin_site)
            request = self.request_factory.post("/owner-admin/quotation/quotemodel/add/")
            request.user = self.operator
            request.tenant = self.tenant
            product_without_default = ProductModel.objects.create(
                tenant=self.tenant,
                name="Valve",
                slug="valve",
                sku_base="VALVE",
            )
            ProductVariantModel.objects.create(
                product=product_without_default,
                sku="VALVE-001",
                price=Decimal("21.00"),
                is_default=False,
            )
            formset_class = inline.get_formset(request, obj=None)
            prefix = "items"
            formset = formset_class(
                data={
                    f"{prefix}-TOTAL_FORMS": "1",
                    f"{prefix}-INITIAL_FORMS": "0",
                    f"{prefix}-MIN_NUM_FORMS": "0",
                    f"{prefix}-MAX_NUM_FORMS": "1000",
                    f"{prefix}-0-product": str(product_without_default.pk),
                    f"{prefix}-0-variant": "",
                    f"{prefix}-0-quantity": "1",
                    f"{prefix}-0-notes": "",
                },
                instance=QuoteModel(tenant=self.tenant, customer_name="Manual"),
                prefix=prefix,
            )

            self.assertFalse(formset.is_valid())
            self.assertIn(
                "Choose a variant or configure one default variant for the selected product.",
                formset.forms[0].errors["variant"],
            )

    def test_quote_item_inline_rejects_zero_quantity(self) -> None:
        """ Verify add-time quote items reject zero quantity through the model-backed inline form. """
        with override("en"):
            inline = QuoteItemModelInline(QuoteModel, owner_admin_site)
            request = self.request_factory.post("/owner-admin/quotation/quotemodel/add/")
            request.user = self.operator
            request.tenant = self.tenant
            formset_class = inline.get_formset(request, obj=None)
            prefix = "items"
            formset = formset_class(
                data={
                    f"{prefix}-TOTAL_FORMS": "1",
                    f"{prefix}-INITIAL_FORMS": "0",
                    f"{prefix}-MIN_NUM_FORMS": "0",
                    f"{prefix}-MAX_NUM_FORMS": "1000",
                    f"{prefix}-0-product": str(self.in_scope_product.pk),
                    f"{prefix}-0-variant": str(self.in_scope_variant.pk),
                    f"{prefix}-0-quantity": "0",
                    f"{prefix}-0-notes": "",
                },
                instance=QuoteModel(tenant=self.tenant, customer_name="Manual"),
                prefix=prefix,
            )

            self.assertFalse(formset.is_valid())
            self.assertIn("Ensure this value is greater than or equal to 1.", formset.forms[0].errors["quantity"])
