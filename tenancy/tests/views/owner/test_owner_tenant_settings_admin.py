""" Tests for the owner tenant settings native change flow. """

from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils.translation import gettext as _
from core.testing.base import LoggedTestCase
from accounts.models import UserModel
from tenancy.choices import TenantRole
from tenancy.models import TenantBrandingModel, TenantMembershipModel, TenantModel


class TestOwnerTenantSettingsAdmin(LoggedTestCase):
    """ Verify owners can reach and use the native owner tenant change form. """

    def setUp(self) -> None:
        """ Create reusable users and one active tenant for the owner settings flow. """
        self.owner = UserModel.objects.create_user(
            username="owner-settings",
            password="test-pass",
            is_staff=True,
            is_active=True,
        )
        self.operator = UserModel.objects.create_user(
            username="operator-settings",
            password="test-pass",
            is_staff=True,
            is_active=True,
        )
        self.tenant = TenantModel.objects.create(name="GEA Trader", slug="gea-trader")

        TenantMembershipModel.objects.create(
            tenant=self.tenant,
            user=self.owner,
            role=TenantRole.OWNER,
            is_active=True,
            is_primary=True,
        )
        TenantMembershipModel.objects.create(
            tenant=self.tenant,
            user=self.operator,
            role=TenantRole.OPERATOR,
            is_active=True,
            is_primary=False,
        )

    def test_owner_can_open_native_change_screen_for_active_tenant(self) -> None:
        """ Verify owners can render the native tenant change form. """
        self.client.force_login(self.owner)
        session = self.client.session
        session["active_tenant_id"] = str(self.tenant.pk)
        session.save()

        response = self.client.get(
            reverse("owner_admin:tenancy_tenantmodel_change", args=(str(self.tenant.pk),))
        )

        self.assertEqual(200, response.status_code)
        self.assertContains(response, "GEA Trader")
        self.assertContains(response, _("Business email"))
        self.assertContains(response, _("Support email"))
        self.assertContains(response, _("Phone number"))
        self.assertContains(response, _("Website"))

    def test_owner_tenant_changelist_redirects_to_active_tenant_change_screen(self) -> None:
        """ Verify the owner tenant changelist redirects to the active tenant change form. """
        self.client.force_login(self.owner)
        session = self.client.session
        session["active_tenant_id"] = str(self.tenant.pk)
        session.save()

        with patch("tenancy.admin.owner.owner_tenant_settings_admin.logger.info") as logger_info_mock:
            response = self.client.get(
                reverse("owner_admin:tenancy_tenantmodel_changelist"),
                follow=False,
            )

        self.assertEqual(302, response.status_code)
        self.assertEqual(
            reverse("owner_admin:tenancy_tenantmodel_change", args=(str(self.tenant.pk),)),
            response.headers["Location"],
        )
        logger_info_mock.assert_called_once()

    def test_operator_cannot_open_native_change_screen(self) -> None:
        """ Verify operators are forbidden from the owner native tenant change screen. """
        self.client.force_login(self.operator)
        session = self.client.session
        session["active_tenant_id"] = str(self.tenant.pk)
        session.save()

        response = self.client.get(
            reverse("owner_admin:tenancy_tenantmodel_change", args=(str(self.tenant.pk),))
        )

        self.assertEqual(403, response.status_code)

    def test_post_creates_branding_record_for_active_tenant(self) -> None:
        """ Verify posting valid inline data creates one branding record for the active tenant. """
        self.client.force_login(self.owner)
        session = self.client.session
        session["active_tenant_id"] = str(self.tenant.pk)
        session.save()

        response = self.client.post(
            reverse("owner_admin:tenancy_tenantmodel_change", args=(str(self.tenant.pk),)),
            {
                "branding-TOTAL_FORMS": "1",
                "branding-INITIAL_FORMS": "0",
                "branding-MIN_NUM_FORMS": "0",
                "branding-MAX_NUM_FORMS": "1",
                "branding-0-display_name": "GEA Trader Pro",
                "branding-0-logo_light": "",
                "branding-0-logo_dark": "",
                "branding-0-icon_light": "",
                "branding-0-icon_dark": "",
                "branding-0-favicon_light": "",
                "branding-0-favicon_dark": "",
                "_save": "Save",
            },
            follow=False,
        )

        self.assertEqual(302, response.status_code)
        branding = TenantBrandingModel.objects.get(tenant=self.tenant)
        self.assertEqual("GEA Trader Pro", branding.display_name)

    def test_post_updates_existing_branding_record_for_active_tenant(self) -> None:
        """ Verify posting valid inline data updates the existing branding record. """
        branding = TenantBrandingModel.objects.create(
            tenant=self.tenant,
            display_name="GEA Trader",
        )

        self.client.force_login(self.owner)
        session = self.client.session
        session["active_tenant_id"] = str(self.tenant.pk)
        session.save()

        response = self.client.post(
            reverse("owner_admin:tenancy_tenantmodel_change", args=(str(self.tenant.pk),)),
            {
                "branding-TOTAL_FORMS": "1",
                "branding-INITIAL_FORMS": "1",
                "branding-MIN_NUM_FORMS": "0",
                "branding-MAX_NUM_FORMS": "1",
                "branding-0-id": str(branding.pk),
                "branding-0-tenant": str(self.tenant.pk),
                "branding-0-display_name": "GEA Trader Updated",
                "branding-0-logo_light": "",
                "branding-0-logo_dark": "",
                "branding-0-icon_light": "",
                "branding-0-icon_dark": "",
                "branding-0-favicon_light": "",
                "branding-0-favicon_dark": "",
                "_save": "Save",
            },
            follow=False,
        )

        self.assertEqual(302, response.status_code)
        branding.refresh_from_db()
        self.assertEqual("GEA Trader Updated", branding.display_name)

    def test_post_accepts_branding_file_uploads(self) -> None:
        """ Verify owners can upload one branding asset through the inline formset. """
        self.client.force_login(self.owner)
        session = self.client.session
        session["active_tenant_id"] = str(self.tenant.pk)
        session.save()

        uploaded_logo = SimpleUploadedFile(
            "logo-light.gif",
            (
                b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00"
                b"\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00"
                b"\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02"
                b"\x44\x01\x00\x3b"
            ),
            content_type="image/gif",
        )

        response = self.client.post(
            reverse("owner_admin:tenancy_tenantmodel_change", args=(str(self.tenant.pk),)),
            {
                "branding-TOTAL_FORMS": "1",
                "branding-INITIAL_FORMS": "0",
                "branding-MIN_NUM_FORMS": "0",
                "branding-MAX_NUM_FORMS": "1",
                "branding-0-display_name": "GEA Trader Upload",
                "branding-0-logo_light": uploaded_logo,
                "branding-0-logo_dark": "",
                "branding-0-icon_light": "",
                "branding-0-icon_dark": "",
                "branding-0-favicon_light": "",
                "branding-0-favicon_dark": "",
                "_save": "Save",
            },
            follow=False,
        )

        self.assertEqual(302, response.status_code)
        branding = TenantBrandingModel.objects.get(tenant=self.tenant)
        self.assertIn("logo-light", branding.logo_light.name)

    def test_post_updates_operational_contact_fields_for_the_active_tenant(self) -> None:
        """ Verify owner settings can update tenant business contact fields without touching branding. """
        self.client.force_login(self.owner)
        session = self.client.session
        session["active_tenant_id"] = str(self.tenant.pk)
        session.save()

        response = self.client.post(
            reverse("owner_admin:tenancy_tenantmodel_change", args=(str(self.tenant.pk),)),
            {
                "business_email": "hello@gea-trader.test",
                "support_email": "support@gea-trader.test",
                "phone_number": "+54 11 5555 4321",
                "website_url": "https://gea-trader.test",
                "branding-TOTAL_FORMS": "0",
                "branding-INITIAL_FORMS": "0",
                "branding-MIN_NUM_FORMS": "0",
                "branding-MAX_NUM_FORMS": "1",
                "_save": "Save",
            },
            follow=False,
        )

        self.assertEqual(302, response.status_code)
        self.tenant.refresh_from_db()
        self.assertEqual("hello@gea-trader.test", self.tenant.business_email)
        self.assertEqual("support@gea-trader.test", self.tenant.support_email)
        self.assertEqual("+54 11 5555 4321", self.tenant.phone_number)
        self.assertEqual("https://gea-trader.test", self.tenant.website_url)
