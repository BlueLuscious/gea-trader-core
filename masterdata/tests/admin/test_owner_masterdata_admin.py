""" Owner admin tests for tenant-scoped masterdata flows. """

from types import SimpleNamespace
from unittest.mock import patch
from django.contrib.auth.models import Permission
from django.test import Client, RequestFactory
from django.urls import reverse
from django.utils.translation import override
from accounts.models import UserModel
from core.adminsites.site_instances import owner_admin_site
from core.testing.base import LoggedTestCase
from masterdata.admin.owner.brand_model_admin import BrandModelAdmin
from masterdata.admin.owner.category_child_model_inline import CategoryChildModelInline
from masterdata.admin.owner.category_model_admin import CategoryModelAdmin
from masterdata.models import BrandModel, CategoryModel
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestOwnerMasterdataAdmin(LoggedTestCase):
    """ Verify the owner masterdata admin stays scoped to the active tenant. """

    def setUp(self) -> None:
        """ Create reusable request factory, tenant, operator, and masterdata fixtures. """
        self.client = Client()
        self.request_factory = RequestFactory()
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        self.operator = UserModel.objects.create_user(
            username="masterdata-operator",
            password="test-pass",
            is_active=True,
            is_staff=True,
        )
        self.outsider = UserModel.objects.create_user(
            username="masterdata-outsider",
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
                codename__in=(
                    "view_brandmodel",
                    "add_brandmodel",
                    "change_brandmodel",
                    "view_categorymodel",
                    "add_categorymodel",
                    "change_categorymodel",
                )
            )
        )
        self.in_scope_brand = BrandModel.objects.create(
            tenant=self.tenant,
            name="GEA",
            slug="gea",
        )
        self.out_of_scope_brand = BrandModel.objects.create(
            tenant=self.other_tenant,
            name="Other",
            slug="other",
        )
        self.in_scope_category = CategoryModel.objects.create(
            tenant=self.tenant,
            name="Industrial",
            slug="industrial",
        )
        self.out_of_scope_category = CategoryModel.objects.create(
            tenant=self.other_tenant,
            name="Legacy",
            slug="legacy",
        )
        self.brand_admin = BrandModelAdmin(BrandModel, owner_admin_site)
        self.category_admin = CategoryModelAdmin(CategoryModel, owner_admin_site)

    def build_request(self, user: UserModel, tenant: TenantModel | None) -> object:
        """ Build one owner-admin request for one user and tenant context.

        Args:
            user: Authenticated actor.
            tenant: Active tenant in scope.

        Returns:
            object: Request object carrying the actor and tenant.
        """
        request = self.request_factory.get("/owner-admin/masterdata/")
        request.user = user
        request.tenant = tenant
        return request

    def test_brand_admin_get_queryset_is_scoped_to_the_active_tenant(self) -> None:
        """ Verify the owner brand queryset only returns brands from the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        with patch("masterdata.admin.owner.brand_model_admin.logger.info") as logger_info_mock:
            queryset = self.brand_admin.get_queryset(request)

        self.assertEqual([self.in_scope_brand], list(queryset))
        logger_info_mock.assert_called_once()

    def test_category_admin_get_queryset_is_scoped_to_the_active_tenant(self) -> None:
        """ Verify the owner category queryset only returns categories from the active tenant. """
        child_category = CategoryModel.objects.create(
            tenant=self.tenant,
            name="Industrial child",
            slug="industrial-child",
            parent=self.in_scope_category,
        )
        request = self.build_request(self.operator, self.tenant)

        with patch("masterdata.admin.owner.category_model_admin.logger.info") as logger_info_mock:
            queryset = self.category_admin.get_queryset(request)

        self.assertEqual([self.in_scope_category, child_category], list(queryset))
        logger_info_mock.assert_called_once()

    def test_category_admin_changelist_only_lists_root_categories(self) -> None:
        """ Verify the owner category changelist stays focused on root categories. """
        CategoryModel.objects.create(
            tenant=self.tenant,
            name="Industrial child",
            slug="industrial-child",
            parent=self.in_scope_category,
        )
        self.client.force_login(self.operator)
        session = self.client.session
        session["active_tenant_id"] = str(self.tenant.pk)
        session.save()

        response = self.client.get(reverse("owner_admin:masterdata_categorymodel_changelist"))

        self.assertEqual(200, response.status_code)
        self.assertContains(response, "Industrial")
        self.assertNotContains(response, "Industrial child")

    def test_brand_admin_get_queryset_logs_when_no_active_tenant_exists(self) -> None:
        """ Verify the owner brand queryset logs when no tenant is bound to the request. """
        request = self.build_request(self.operator, tenant=None)

        with patch("masterdata.admin.owner.brand_model_admin.logger.info") as logger_info_mock:
            queryset = self.brand_admin.get_queryset(request)

        self.assertEqual([], list(queryset))
        logger_info_mock.assert_called_once()

    def test_category_admin_get_queryset_logs_when_no_active_tenant_exists(self) -> None:
        """ Verify the owner category queryset logs when no tenant is bound to the request. """
        request = self.build_request(self.operator, tenant=None)

        with patch("masterdata.admin.owner.category_model_admin.logger.info") as logger_info_mock:
            queryset = self.category_admin.get_queryset(request)

        self.assertEqual([], list(queryset))
        logger_info_mock.assert_called_once()

    def test_brand_admin_save_model_assigns_the_active_tenant_on_create(self) -> None:
        """ Verify owner-created brands inherit the active tenant automatically. """
        request = self.build_request(self.operator, self.tenant)
        brand = BrandModel(name="North", slug="north")

        with patch("masterdata.admin.owner.brand_model_admin.logger.info") as logger_info_mock:
            self.brand_admin.save_model(request, brand, form=None, change=False)

        self.assertEqual(self.tenant, brand.tenant)
        logger_info_mock.assert_called_once()

    def test_category_admin_save_model_assigns_the_active_tenant_on_create(self) -> None:
        """ Verify owner-created categories inherit the active tenant automatically. """
        request = self.build_request(self.operator, self.tenant)
        category = CategoryModel(name="Pumps", slug="pumps")

        with patch("masterdata.admin.owner.category_model_admin.logger.info") as logger_info_mock:
            self.category_admin.save_model(request, category, form=None, change=False)

        self.assertEqual(self.tenant, category.tenant)
        logger_info_mock.assert_called_once()

    def test_brand_permissions_reject_objects_from_other_tenants(self) -> None:
        """ Verify brand object permissions stay scoped to the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(self.brand_admin.has_view_permission(request, self.in_scope_brand))
        self.assertTrue(self.brand_admin.has_change_permission(request, self.in_scope_brand))
        self.assertFalse(self.brand_admin.has_view_permission(request, self.out_of_scope_brand))
        self.assertFalse(self.brand_admin.has_change_permission(request, self.out_of_scope_brand))

    def test_category_permissions_reject_objects_from_other_tenants(self) -> None:
        """ Verify category object permissions stay scoped to the active tenant. """
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(self.category_admin.has_view_permission(request, self.in_scope_category))
        self.assertTrue(self.category_admin.has_change_permission(request, self.in_scope_category))
        self.assertFalse(self.category_admin.has_view_permission(request, self.out_of_scope_category))
        self.assertFalse(self.category_admin.has_change_permission(request, self.out_of_scope_category))

    def test_module_and_add_permissions_require_masterdata_access(self) -> None:
        """ Verify owner masterdata modules stay blocked without tenant membership. """
        member_request = self.build_request(self.operator, self.tenant)
        outsider_request = self.build_request(self.outsider, self.tenant)

        self.assertTrue(self.brand_admin.has_module_permission(member_request))
        self.assertTrue(self.brand_admin.has_add_permission(member_request))
        self.assertTrue(self.category_admin.has_module_permission(member_request))
        self.assertTrue(self.category_admin.has_add_permission(member_request))
        self.assertFalse(self.brand_admin.has_module_permission(outsider_request))
        self.assertFalse(self.brand_admin.has_add_permission(outsider_request))
        self.assertFalse(self.category_admin.has_module_permission(outsider_request))
        self.assertFalse(self.category_admin.has_add_permission(outsider_request))

    def test_category_parent_field_limits_choices_to_the_active_tenant(self) -> None:
        """ Verify category parent choices only expose rows from the active tenant. """
        request = self.build_request(self.operator, self.tenant)
        form_field = self.category_admin.formfield_for_foreignkey(
            CategoryModel._meta.get_field("parent"),
            request,
        )

        self.assertEqual([self.in_scope_category], list(form_field.queryset))

    def test_category_parent_field_excludes_the_current_object_on_change(self) -> None:
        """ Verify category parent choices do not allow a category to parent itself. """
        request = self.build_request(self.operator, self.tenant)
        request.resolver_match = SimpleNamespace(kwargs={"object_id": str(self.in_scope_category.pk)})

        form_field = self.category_admin.formfield_for_foreignkey(
            CategoryModel._meta.get_field("parent"),
            request,
        )

        self.assertEqual([], list(form_field.queryset))

    def test_category_parent_field_excludes_descendants_on_change(self) -> None:
        """ Verify category parent choices do not allow one category to parent under its own descendants. """
        child_category = CategoryModel.objects.create(
            tenant=self.tenant,
            name="Sub industrial",
            slug="sub-industrial",
            parent=self.in_scope_category,
        )
        grandchild_category = CategoryModel.objects.create(
            tenant=self.tenant,
            name="Leaf industrial",
            slug="leaf-industrial",
            parent=child_category,
        )
        unrelated_category = CategoryModel.objects.create(
            tenant=self.tenant,
            name="Portable",
            slug="portable",
        )
        request = self.build_request(self.operator, self.tenant)
        request.resolver_match = SimpleNamespace(kwargs={"object_id": str(self.in_scope_category.pk)})

        form_field = self.category_admin.formfield_for_foreignkey(
            CategoryModel._meta.get_field("parent"),
            request,
        )

        self.assertEqual([unrelated_category], list(form_field.queryset))
        self.assertNotIn(child_category, form_field.queryset)
        self.assertNotIn(grandchild_category, form_field.queryset)

    def test_category_child_inline_is_available_during_add_and_change_flows(self) -> None:
        """ Verify the child-category inline stays available across add and change flows. """
        inline = CategoryChildModelInline(CategoryModel, owner_admin_site)
        request = self.build_request(self.operator, self.tenant)

        self.assertTrue(inline.has_add_permission(request, obj=None))
        self.assertEqual(1, inline.get_extra(request, obj=None))
        self.assertTrue(inline.has_add_permission(request, obj=self.in_scope_category))
        self.assertEqual(1, inline.get_extra(request, obj=self.in_scope_category))

    def test_category_child_inline_assigns_parent_tenant_on_create(self) -> None:
        """ Verify inline-created child categories inherit both the parent and tenant automatically. """
        inline = CategoryChildModelInline(CategoryModel, owner_admin_site)
        request = self.build_request(self.operator, self.tenant)
        formset_class = inline.get_formset(request, obj=self.in_scope_category)
        prefix = formset_class.get_default_prefix()
        formset = formset_class(
            data={
                f"{prefix}-TOTAL_FORMS": "1",
                f"{prefix}-INITIAL_FORMS": "0",
                f"{prefix}-MIN_NUM_FORMS": "0",
                f"{prefix}-MAX_NUM_FORMS": "1000",
                f"{prefix}-0-name": "Portable",
                f"{prefix}-0-slug": "portable",
                f"{prefix}-0-sort_order": "5",
                f"{prefix}-0-is_active": "on",
            },
            instance=self.in_scope_category,
            prefix=prefix,
        )

        self.assertTrue(formset.is_valid(), formset.errors)

        with patch("masterdata.admin.owner.category_child_model_inline_formset.logger.info") as logger_info_mock:
            child_category = formset.save()[0]

        self.assertEqual(self.tenant, child_category.tenant)
        self.assertEqual(self.in_scope_category, child_category.parent)
        logger_info_mock.assert_called_once()

    def test_category_admin_form_accepts_parent_from_the_active_tenant_on_add(self) -> None:
        """ Verify the owner category form can validate one in-tenant parent during adds. """
        request = self.build_request(self.operator, self.tenant)
        form_class = self.category_admin.get_form(request)
        form = form_class(
            data={
                "name": "Holis 4",
                "slug": "holis-4",
                "description": "",
                "parent": str(self.in_scope_category.pk),
                "sort_order": "0",
                "is_active": "on",
                "is_featured": "on",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(self.tenant, form.instance.tenant)
        self.assertTrue(form.instance.is_featured)

    def test_category_admin_form_rejects_duplicate_slug_inside_active_tenant(self) -> None:
        """ Verify the owner category form reports duplicate slugs as a clear field error. """
        request = self.build_request(self.operator, self.tenant)
        form_class = self.category_admin.get_form(request)
        form = form_class(
            data={
                "name": "Industrial duplicate",
                "slug": self.in_scope_category.slug,
                "description": "",
                "parent": "",
                "sort_order": "0",
                "is_active": "on",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("slug", form.errors)
        self.assertIn("already used by another category", form.errors["slug"][0])

    def test_category_admin_splits_storefront_and_organization_fields(self) -> None:
        """ Verify the owner category admin keeps storefront fields separate from hierarchy controls. """
        with override("en"):
            fieldsets = self.category_admin.get_fieldsets(self.build_request(self.operator, self.tenant))

            self.assertEqual(
                [fieldset[0] for fieldset in fieldsets],
                [
                    "Category details",
                    "Storefront presentation",
                    "Catalog organization",
                    "Advanced details",
                ],
            )
            self.assertEqual(fieldsets[0][1]["fields"], (("name", "slug"), "description"))
            self.assertEqual(fieldsets[1][1]["fields"], ("banner", "is_featured"))
            self.assertEqual(fieldsets[2][1]["fields"], (("parent", "sort_order"), "is_active"))

    def test_owner_category_add_view_can_create_parent_and_subcategory_in_one_post(self) -> None:
        """ Verify the owner add view can persist one category and one inline child together. """
        self.client.force_login(self.operator)
        session = self.client.session
        session["active_tenant_id"] = str(self.tenant.pk)
        session.save()

        response = self.client.post(
            reverse("owner_admin:masterdata_categorymodel_add"),
            data={
                "name": "Holis 4",
                "slug": "holis-4",
                "description": "",
                "parent": str(self.in_scope_category.pk),
                "sort_order": "0",
                "is_active": "on",
                "children-TOTAL_FORMS": "1",
                "children-INITIAL_FORMS": "0",
                "children-MIN_NUM_FORMS": "0",
                "children-MAX_NUM_FORMS": "1000",
                "children-0-name": "Holis 4 child",
                "children-0-slug": "holis-4-child",
                "children-0-sort_order": "1",
                "children-0-is_active": "on",
            },
        )

        self.assertEqual(302, response.status_code)

        created_parent = CategoryModel.objects.get(tenant=self.tenant, slug="holis-4")
        created_child = CategoryModel.objects.get(tenant=self.tenant, slug="holis-4-child")

        self.assertEqual(self.in_scope_category, created_parent.parent)
        self.assertEqual(created_parent, created_child.parent)
