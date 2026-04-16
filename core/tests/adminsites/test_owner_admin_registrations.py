""" Tests for owner admin site model registrations. """

from decimal import Decimal
from django.contrib.auth.models import Permission
from django.test import RequestFactory
from django.utils.translation import gettext as _
from accounts.admin.owner.user_model_admin import OwnerUserModelAdmin
from accounts.models import UserModel
from catalog.admin.owner.product_image_model_inline import ProductImageModelInline
from catalog.admin.owner.product_model_admin import ProductModelAdmin
from catalog.admin.owner.product_variant_model_inline import ProductVariantModelInline
from catalog.models import ProductModel
from core.adminsites.site_instances import owner_admin_site
from core.testing.base import LoggedTestCase
from catalog.models import ProductVariantModel
from masterdata.admin.owner.brand_model_admin import BrandModelAdmin
from masterdata.admin.owner.category_model_admin import CategoryModelAdmin
from masterdata.models import BrandModel, CategoryModel
from tenancy.models import TenantMembershipModel
from tenancy.models import TenantModel
from quotation.admin.owner.quote_item_model_inline import QuoteItemModelInline
from quotation.admin.owner.quote_model_admin_form import QuoteModelAdminForm
from quotation.admin.owner.quote_model_admin import QuoteModelAdmin
from quotation.models import QuoteModel
from quotation.models import QuoteItemModel


class TestOwnerAdminRegistrations(LoggedTestCase):
    """ Verify that owner admin registrations stay limited to the curated surface. """

    def setUp(self) -> None:
        """ Create the request factory and authenticated owner used by the tests. """
        self.request_factory = RequestFactory()
        self.owner_account = UserModel.objects.create(
            username="owner-admin",
            email="owner@example.com",
            is_active=True,
            is_staff=True,
        )
        self.master_account = UserModel.objects.create(
            username="master-admin",
            email="master@example.com",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        self.owner_user = type(
            "OwnerUser",
            (),
            {
                "is_active": True,
                "is_superuser": False,
                "is_staff": True,
                "pk": self.owner_account.pk,
                "has_module_perms": lambda self, app_label: True,
                "has_perm": lambda self, perm: True,
            },
        )()

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for owner-admin catalog fixtures.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_owner_admin_registers_curated_models(self) -> None:
        """ Verify the owner admin site currently registers the curated user, catalog, masterdata, and quote models. """
        self.assertIn(UserModel, owner_admin_site._registry)
        self.assertIn(ProductModel, owner_admin_site._registry)
        self.assertIn(BrandModel, owner_admin_site._registry)
        self.assertIn(CategoryModel, owner_admin_site._registry)
        self.assertIn(QuoteModel, owner_admin_site._registry)

    def test_owner_admin_sidebar_navigation_includes_registered_links(self) -> None:
        """ Verify the owner sidebar exposes the registered user, catalog, masterdata, and quote changelist links. """
        request = self.request_factory.get("/owner-admin/")
        request.user = self.owner_user
        navigation = owner_admin_site.get_sidebar_navigation(request)

        item_links = {
            item["link"]
            for group in navigation
            for item in group["items"]
        }

        self.assertIn("/owner-admin/accounts/usermodel/", item_links)
        self.assertIn("/owner-admin/catalog/productmodel/", item_links)
        self.assertIn("/owner-admin/masterdata/brandmodel/", item_links)
        self.assertIn("/owner-admin/masterdata/categorymodel/", item_links)
        self.assertIn("/owner-admin/quotation/quotemodel/", item_links)

    def test_owner_users_flow_requires_expected_django_permissions(self) -> None:
        """ Verify the owner users flow is backed by the expected Django model permissions. """
        expected_permissions = {
            "add_usermodel",
            "change_usermodel",
            "view_usermodel",
        }

        found_permissions = set(
            Permission.objects.filter(
                codename__in=expected_permissions,
                content_type__app_label="accounts",
            ).values_list("codename", flat=True)
        )

        self.assertEqual(expected_permissions, found_permissions)

    def test_owner_user_admin_hides_superusers_and_disables_delete(self) -> None:
        """ Verify the owner user admin excludes superusers and avoids hard delete. """
        user_admin = OwnerUserModelAdmin(UserModel, owner_admin_site)
        tenant = TenantModel.objects.create(name="Owner Tenant", slug="owner-tenant")
        TenantMembershipModel.objects.create(
            user=self.owner_account,
            tenant=tenant,
            role="owner",
            is_active=True,
            is_primary=True,
        )
        request = self.request_factory.get("/owner-admin/accounts/usermodel/")
        request.user = self.owner_account
        request.tenant = tenant

        queryset = user_admin.get_queryset(request)

        self.assertIn(self.owner_account, queryset)
        self.assertNotIn(self.master_account, queryset)
        self.assertFalse(user_admin.has_delete_permission(request))

    def test_owner_user_admin_protects_the_current_owner_from_self_demoting(self) -> None:
        """ Verify owners cannot remove their own admin access from the edit screen. """
        user_admin = OwnerUserModelAdmin(UserModel, owner_admin_site)
        request = self.request_factory.get(f"/owner-admin/accounts/usermodel/{self.owner_account.pk}/change/")
        request.user = self.owner_user

        readonly_fields = user_admin.get_readonly_fields(request, obj=self.owner_account)

        self.assertIn("is_active", readonly_fields)
        self.assertIn("is_staff", readonly_fields)

    def test_owner_user_admin_uses_tabs_for_sections(self) -> None:
        """ Verify the owner user admin uses Unfold tabs for guided account editing. """
        user_admin = OwnerUserModelAdmin(UserModel, owner_admin_site)

        change_fieldset_classes = [fieldset[1].get("classes", ()) for fieldset in user_admin.fieldsets]
        add_fieldset_classes = [fieldset[1].get("classes", ()) for fieldset in user_admin.add_fieldsets]

        self.assertEqual(3, change_fieldset_classes.count(("tab",)))
        self.assertEqual(2, add_fieldset_classes.count(("tab",)))

    def test_owner_user_admin_loads_custom_css_for_fieldset_description_spacing(self) -> None:
        """ Verify the owner user admin loads the CSS tweak for fieldset descriptions. """
        user_admin = OwnerUserModelAdmin(UserModel, owner_admin_site)

        self.assertIn(
            "accounts/admin/owner/user_model_admin.css",
            str(user_admin.media),
        )

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
        tenant = self._create_tenant("owner-products")
        brand = BrandModel.objects.create(tenant=tenant, name="Brand", slug="brand")
        category = CategoryModel.objects.create(tenant=tenant, name="Category", slug="category")
        first_product = ProductModel.objects.create(tenant=tenant, name="First", slug="first", brand=brand, category=category)
        second_product = ProductModel.objects.create(tenant=tenant, name="Second", slug="second", brand=brand, category=category)
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

    def test_owner_masterdata_flows_require_expected_django_permissions(self) -> None:
        """ Verify the owner masterdata flows are backed by the expected Django model permissions. """
        expected_permissions = {
            "add_brandmodel",
            "change_brandmodel",
            "view_brandmodel",
            "add_categorymodel",
            "change_categorymodel",
            "view_categorymodel",
        }

        found_permissions = set(
            Permission.objects.filter(
                codename__in=expected_permissions,
                content_type__app_label="masterdata",
            ).values_list("codename", flat=True)
        )

        self.assertEqual(expected_permissions, found_permissions)

    def test_owner_masterdata_admin_prefers_guided_delete_policy(self) -> None:
        """ Verify the owner masterdata flows disable hard delete where active state already exists. """
        brand_admin = BrandModelAdmin(BrandModel, owner_admin_site)
        category_admin = CategoryModelAdmin(CategoryModel, owner_admin_site)

        request = self.request_factory.get("/owner-admin/masterdata/")
        request.user = self.owner_user

        self.assertFalse(brand_admin.has_delete_permission(request))
        self.assertFalse(category_admin.has_delete_permission(request))

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

    def test_owner_quotes_flow_requires_expected_django_permissions(self) -> None:
        """ Verify the owner quotes flow is backed by the expected Django model permissions. """
        expected_permissions = {
            "add_quotemodel",
            "view_quotemodel",
            "change_quotemodel",
            "add_quoteitemmodel",
            "view_quoteitemmodel",
        }

        found_permissions = set(
            Permission.objects.filter(
                codename__in=expected_permissions,
                content_type__app_label="quotation",
            ).values_list("codename", flat=True)
        )

        self.assertEqual(expected_permissions, found_permissions)

    def test_owner_quote_admin_prefers_guided_delete_and_freezes_items_after_creation(self) -> None:
        """ Verify the owner quote flow allows add-time composition and freezes items later. """
        quote_admin = QuoteModelAdmin(QuoteModel, owner_admin_site)
        item_inline = QuoteItemModelInline(QuoteModel, owner_admin_site)

        request = self.request_factory.get("/owner-admin/quotation/quotemodel/")
        request.user = self.owner_user

        self.assertFalse(quote_admin.has_delete_permission(request))
        self.assertFalse(item_inline.can_delete)
        self.assertTrue(item_inline.has_add_permission(request, obj=None))
        existing_quote = QuoteModel(tenant=self._create_tenant("owner-quote-delete-policy"), customer_name="Owner Quote")
        self.assertFalse(item_inline.has_add_permission(request, obj=existing_quote))
        self.assertEqual((), item_inline.get_readonly_fields(request, obj=None))
        self.assertIn("product_name_snapshot", item_inline.get_readonly_fields(request, obj=existing_quote))

    def test_owner_quote_admin_uses_quote_items_as_top_level_tab(self) -> None:
        """ Verify quote items are exposed as a main inline tab beside the general form. """
        quote_admin = QuoteModelAdmin(QuoteModel, owner_admin_site)
        request = self.request_factory.get("/owner-admin/quotation/quotemodel/add/")
        request.user = self.owner_user

        fieldset_classes = [fieldset[1].get("classes", ()) for fieldset in quote_admin.get_fieldsets(request, obj=None)]

        self.assertIn(("tab",), fieldset_classes)
        self.assertEqual(2, fieldset_classes.count(("tab",)))
        self.assertTrue(QuoteItemModelInline.tab)

    def test_owner_quote_admin_loads_custom_css_for_fieldset_description_spacing(self) -> None:
        """ Verify the owner quote admin loads the CSS tweak for fieldset descriptions. """
        quote_admin = QuoteModelAdmin(QuoteModel, owner_admin_site)

        self.assertIn(
            "quotation/admin/owner/quote_model_admin.css",
            str(quote_admin.media),
        )

    def test_owner_quote_admin_reveals_origin_and_timeline_only_after_creation(self) -> None:
        """ Verify origin and timeline fieldsets appear only on the change view. """
        quote_admin = QuoteModelAdmin(QuoteModel, owner_admin_site)
        request = self.request_factory.get("/owner-admin/quotation/quotemodel/")
        request.user = self.owner_user

        add_titles = [fieldset[0] for fieldset in quote_admin.get_fieldsets(request, obj=None)]
        change_titles = [fieldset[0] for fieldset in quote_admin.get_fieldsets(request, obj=QuoteModel(tenant=self._create_tenant("owner-quote-timeline")))]

        self.assertEqual([_("Customer"), _("Quote details")], add_titles)
        self.assertEqual([_("Customer"), _("Quote details"), _("Origin"), _("Timeline")], change_titles)

    def test_owner_quote_item_formset_populates_snapshot_fields_from_selected_catalog_data(self) -> None:
        """ Verify add-time quote items snapshot the chosen product and variant data automatically. """
        tenant = self._create_tenant("owner-quote-items")
        brand = BrandModel.objects.create(tenant=tenant, name="Brand", slug="brand-inline")
        category = CategoryModel.objects.create(tenant=tenant, name="Category", slug="category-inline")
        product = ProductModel.objects.create(tenant=tenant, name="Pump", slug="pump", sku_base="PUMP", brand=brand, category=category)
        variant = ProductVariantModel.objects.create(
            product=product,
            sku="PUMP-001",
            attributes_json={"size": "L"},
            price=Decimal("42.50"),
        )

        inline = QuoteItemModelInline(QuoteModel, owner_admin_site)
        request = self.request_factory.post("/owner-admin/quotation/quotemodel/add/")
        request.user = self.owner_user
        formset_class = inline.get_formset(request, obj=None)
        prefix = QuoteItemModel._meta.model_name + "_set"
        formset = formset_class(
            data={
                f"{prefix}-TOTAL_FORMS": "1",
                f"{prefix}-INITIAL_FORMS": "0",
                f"{prefix}-MIN_NUM_FORMS": "0",
                f"{prefix}-MAX_NUM_FORMS": "1000",
                f"{prefix}-0-product": str(product.pk),
                f"{prefix}-0-variant": str(variant.pk),
                f"{prefix}-0-quantity": "2",
                f"{prefix}-0-notes": "Urgent",
            },
            instance=QuoteModel(tenant=tenant, customer_name="Manual"),
            prefix=prefix,
        )

        self.assertTrue(formset.is_valid(), formset.errors)
        item = formset.save(commit=False)[0]

        self.assertEqual(product.name, item.product_name_snapshot)
        self.assertEqual(variant.sku, item.sku_snapshot)
        self.assertEqual({"size": "L"}, item.attributes_snapshot)
        self.assertEqual(variant.price, item.unit_price_snapshot)

    def test_owner_quote_form_requires_customer_name_and_one_contact_channel(self) -> None:
        """ Verify manual owner quotes require a name plus at least one contact method. """
        form = QuoteModelAdminForm(
            data={
                "status": "draft",
                "customer_name": "",
                "customer_email": "",
                "customer_phone": "",
                "company_name": "",
                "tax_id": "",
                "notes": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("customer_name", form.errors)
        self.assertIn("customer_email", form.errors)
        self.assertIn("customer_phone", form.errors)

    def test_owner_quote_form_accepts_email_without_phone(self) -> None:
        """ Verify manual owner quotes remain valid with a customer name and one contact channel. """
        form = QuoteModelAdminForm(
            data={
                "status": "draft",
                "customer_name": "Lucio",
                "customer_email": "lucio@example.com",
                "customer_phone": "",
                "company_name": "",
                "tax_id": "",
                "notes": "",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
