""" Owner admin tests for tenant-scoped accounts flows. """

from unittest.mock import patch
from django.contrib.auth.models import Group, Permission
from django.test import Client, RequestFactory
from django.urls import reverse
from django.utils.translation import gettext as _, override
from core.adminsites.site_instances import owner_admin_site
from core.testing.base import LoggedTestCase
from accounts.admin.owner.group_admin import OwnerGroupAdmin
from accounts.admin.owner.tenant_membership_inline import TenantMembershipInline
from accounts.admin.owner.user_model_admin import OwnerUserModelAdmin
from accounts.models import UserModel
from tenancy.choices import TenantRole
from tenancy.models import TenantGroupModel, TenantMembershipModel, TenantModel


class TestOwnerAccountsAdmin(LoggedTestCase):
    """ Verify tenant-scoped behavior for owner users and groups. """

    def setUp(self) -> None:
        """ Create reusable request, owner, tenants, groups and permissions. """
        self.request_factory = RequestFactory()
        self.client = Client()
        self.owner = UserModel.objects.create_user(
            username="owner",
            password="test-pass",
            is_staff=True,
            is_active=True,
        )
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        TenantMembershipModel.objects.create(
            tenant=self.tenant,
            user=self.owner,
            role=TenantRole.OWNER,
            is_active=True,
            is_primary=True,
        )
        self.tenant_user = UserModel.objects.create_user(
            username="tenant-user",
            password="test-pass",
            is_staff=True,
            is_active=True,
        )
        self.other_tenant_user = UserModel.objects.create_user(
            username="other-tenant-user",
            password="test-pass",
            is_staff=True,
            is_active=True,
        )
        self.non_owner = UserModel.objects.create_user(
            username="non-owner",
            password="test-pass",
            is_staff=True,
            is_active=True,
        )
        self.platform_member = UserModel.objects.create_user(
            username="platform-member",
            password="test-pass",
            is_staff=True,
            is_active=True,
        )
        TenantMembershipModel.objects.create(
            tenant=self.tenant,
            user=self.tenant_user,
            role=TenantRole.OPERATOR,
            is_active=True,
        )
        TenantMembershipModel.objects.create(
            tenant=self.other_tenant,
            user=self.other_tenant_user,
            role=TenantRole.OPERATOR,
            is_active=True,
        )
        TenantMembershipModel.objects.create(
            tenant=self.tenant,
            user=self.non_owner,
            role=TenantRole.OPERATOR,
            is_active=True,
        )
        TenantMembershipModel.objects.create(
            tenant=self.tenant,
            user=self.platform_member,
            role=TenantRole.MASTER,
            is_active=True,
        )
        self.sales_group = Group.objects.create(name="Sales")
        self.accounts_group = Group.objects.create(name="Accounts")
        TenantGroupModel.objects.create(tenant=self.tenant, group=self.sales_group)
        TenantGroupModel.objects.create(tenant=self.other_tenant, group=self.accounts_group)

        allowed_permission_codenames = (
            "view_usermodel",
            "add_usermodel",
            "change_usermodel",
            "view_group",
            "add_group",
            "change_group",
            "delete_group",
            "view_tenantgroupmodel",
            "add_tenantgroupmodel",
            "change_tenantgroupmodel",
            "delete_tenantgroupmodel",
            "view_tenantmodel",
        )
        self.owner.user_permissions.set(Permission.objects.filter(codename__in=allowed_permission_codenames))

        self.user_admin = OwnerUserModelAdmin(UserModel, owner_admin_site)
        self.group_admin = OwnerGroupAdmin(Group, owner_admin_site)
        self.membership_inline = TenantMembershipInline(UserModel, owner_admin_site)

    def build_request(self) -> object:
        """ Build one owner-admin request scoped to the primary tenant.

        Returns:
            object: Request object with authenticated owner and active tenant.
        """
        request = self.request_factory.get("/owner-admin/")
        request.user = self.owner
        request.tenant = self.tenant
        return request

    def build_non_owner_request(self) -> object:
        """ Build one owner-admin request for a non-owner tenant member.

        Returns:
            object: Request object with authenticated non-owner user and active tenant.
        """
        request = self.request_factory.get("/owner-admin/")
        request.user = self.non_owner
        request.tenant = self.tenant
        return request

    def test_owner_user_admin_filters_group_choices_to_the_active_tenant(self) -> None:
        """ Verify the owner user admin exposes only tenant-scoped groups. """
        request = self.build_request()

        with patch("accounts.admin.owner.user_model_admin.logger.info") as logger_info_mock:
            form_field = self.user_admin.formfield_for_manytomany(UserModel._meta.get_field("groups"), request)

        self.assertEqual([self.sales_group], list(form_field.queryset))
        logger_info_mock.assert_called_once()

    def test_owner_group_admin_queryset_is_scoped_to_the_active_tenant(self) -> None:
        """ Verify the owner group admin lists only groups bound to the active tenant. """
        request = self.build_request()

        with patch("accounts.admin.owner.group_admin.logger.info") as logger_info_mock:
            self.assertEqual([self.sales_group], list(self.group_admin.get_queryset(request)))

        logger_info_mock.assert_called_once()

    def test_owner_user_admin_queryset_is_scoped_to_the_active_tenant(self) -> None:
        """ Verify the owner user admin lists only users bound to the active tenant. """
        request = self.build_request()

        with patch("accounts.admin.owner.user_model_admin.logger.info") as logger_info_mock:
            visible_users = list(self.user_admin.get_queryset(request))

        self.assertIn(self.owner, visible_users)
        self.assertIn(self.tenant_user, visible_users)
        self.assertIn(self.non_owner, visible_users)
        self.assertNotIn(self.other_tenant_user, visible_users)
        self.assertNotIn(self.platform_member, visible_users)
        logger_info_mock.assert_called_once()

    def test_owner_group_admin_creates_a_tenant_binding_on_add(self) -> None:
        """ Verify creating a group from owner admin also creates the tenant binding. """
        request = self.build_request()
        group = Group(name="Support")
        form = OwnerGroupAdmin.form(data={"name": "Support"})
        self.assertTrue(form.is_valid())

        with patch("accounts.admin.owner.group_admin.logger.info") as logger_info_mock:
            self.group_admin.save_model(request, group, form, change=False)

        self.assertTrue(TenantGroupModel.objects.filter(tenant=self.tenant, group=group).exists())
        logger_info_mock.assert_called_once()

    def test_owner_group_admin_filters_permissions_to_the_permissions_the_owner_holds(self) -> None:
        """ Verify the owner group admin exposes every permission already held by the owner. """
        request = self.build_request()

        with patch("accounts.admin.owner.group_admin.logger.info") as group_logger_mock:
            form_field = self.group_admin.formfield_for_manytomany(Group._meta.get_field("permissions"), request)
        visible_codenames = list(form_field.queryset.values_list("codename", flat=True))

        self.assertIn("view_usermodel", visible_codenames)
        self.assertIn("change_group", visible_codenames)
        self.assertIn("view_tenantgroupmodel", visible_codenames)
        self.assertIn("view_tenantmodel", visible_codenames)
        group_logger_mock.assert_called_once()

    def test_owner_group_admin_translates_permission_option_labels(self) -> None:
        """ Verify the permission chooser uses translated, user-friendly labels. """
        request = self.build_request()
        permission = Permission.objects.get(codename="view_tenantgroupmodel")

        with override("es"):
            form_field = self.group_admin.formfield_for_manytomany(Group._meta.get_field("permissions"), request)
            label = form_field.label_from_instance(permission)

        self.assertEqual("Acceso al negocio | Grupo del negocio | Puede ver grupo del negocio", label)

    def test_non_owner_tenant_member_cannot_manage_owner_users_or_groups(self) -> None:
        """ Verify non-owner tenant members cannot administer owner accounts surfaces. """
        request = self.build_non_owner_request()

        self.assertFalse(self.user_admin.has_module_permission(request))
        self.assertFalse(self.user_admin.has_add_permission(request))
        self.assertFalse(self.user_admin.has_view_permission(request))
        self.assertFalse(self.group_admin.has_module_permission(request))
        self.assertFalse(self.group_admin.has_add_permission(request))
        self.assertFalse(self.group_admin.has_view_permission(request))

    def test_non_owner_tenant_member_cannot_delegate_permissions(self) -> None:
        """ Verify non-owner tenant members see no delegable group permissions. """
        request = self.build_non_owner_request()

        with patch("accounts.admin.owner.group_admin.logger.info") as logger_info_mock:
            form_field = self.group_admin.formfield_for_manytomany(Group._meta.get_field("permissions"), request)

        self.assertEqual([], list(form_field.queryset))
        logger_info_mock.assert_called_once()

    def test_owner_membership_inline_limits_role_choices_to_owner_and_operator(self) -> None:
        """ Verify the owner membership inline exposes only owner-managed tenant roles. """
        form = self.membership_inline.form()

        self.assertEqual(
            [(TenantRole.OWNER, _("Owner")), (TenantRole.OPERATOR, _("Operator"))],
            list(form.fields["role"].choices),
        )

    def test_owner_membership_inline_creates_active_tenant_membership_on_save(self) -> None:
        """ Verify the membership inline saves one tenant-scoped membership for the active tenant. """
        request = self.build_request()
        new_user = UserModel.objects.create_user(
            username="new-operator",
            email="new-operator@example.com",
            first_name="New",
            last_name="Operator",
            password="test-pass",
            is_staff=True,
            is_active=True,
        )
        formset_class = self.membership_inline.get_formset(request, obj=new_user)
        prefix = formset_class.get_default_prefix()
        formset = formset_class(
            data={
                f"{prefix}-TOTAL_FORMS": "1",
                f"{prefix}-INITIAL_FORMS": "0",
                f"{prefix}-MIN_NUM_FORMS": "0",
                f"{prefix}-MAX_NUM_FORMS": "1",
                f"{prefix}-0-role": TenantRole.OPERATOR,
                f"{prefix}-0-is_active": "on",
            },
            instance=new_user,
            prefix=prefix,
            request=request,
        )

        self.assertTrue(formset.is_valid(), formset.errors)
        with patch("accounts.admin.owner.tenant_membership_inline_formset.logger.info") as logger_info_mock:
            formset.save()

        self.assertTrue(
            TenantMembershipModel.objects.filter(
                tenant=self.tenant,
                user=new_user,
                role=TenantRole.OPERATOR,
                is_active=True,
            ).exists()
        )
        logger_info_mock.assert_called_once()

    def test_owner_admin_add_view_creates_active_tenant_membership(self) -> None:
        """ Verify the owner add view persists the tenant membership inline on user creation. """
        self.client.force_login(self.owner)
        session = self.client.session
        session["active_tenant_id"] = str(self.tenant.pk)
        session.save()

        response = self.client.post(
            reverse("owner_admin:accounts_usermodel_add"),
            data={
                "username": "new-inline-user",
                "email": "new-inline-user@example.com",
                "first_name": "New",
                "last_name": "Inline",
                "password1": "strong-test-pass-123",
                "password2": "strong-test-pass-123",
                "is_active": "on",
                "is_staff": "on",
                "tenant_memberships-TOTAL_FORMS": "1",
                "tenant_memberships-INITIAL_FORMS": "0",
                "tenant_memberships-MIN_NUM_FORMS": "1",
                "tenant_memberships-MAX_NUM_FORMS": "1",
                "tenant_memberships-0-role": TenantRole.OPERATOR,
                "tenant_memberships-0-is_active": "on",
            },
        )

        self.assertEqual(302, response.status_code)
        created_user = UserModel.objects.get(username="new-inline-user")
        self.assertTrue(
            TenantMembershipModel.objects.filter(
                tenant=self.tenant,
                user=created_user,
                role=TenantRole.OPERATOR,
                is_active=True,
            ).exists()
        )
