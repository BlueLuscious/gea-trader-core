""" Unit tests for tenant-aware media storage helpers. """

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from django.core.files.base import ContentFile
from core.config.storage import MediaStorageAdapterResolver
from core.config.storage.media_storage.backends.tenant_aware_media_storage_mixin import TenantAwareMediaStorageMixin
from core.config.storage.media_storage.backends.tenant_file_system_storage import TenantFileSystemStorage
from core.config.storage.media_storage.paths.tenant_media_path_builder import TenantMediaPathBuilder
from tenancy.runtime import ActiveTenantContext
from core.testing.base import LoggedSimpleTestCase
from tenancy.models import TenantModel


class FakeRemoteMediaStorageBase:
    """ Mimic a remote storage backend that prefixes object names with one location. """

    location = "media"

    def save(
        self,
        name: str | None,
        content: ContentFile,
        max_length: int | None = None,
    ) -> str:
        """ Return the final saved object name without touching it further.

        Args:
            name: Requested object name.
            content: Uploaded file payload.
            max_length: Optional max path length.

        Returns:
            str: Final object name.
        """
        del content, max_length
        return str(name)

    def generate_filename(self, filename: str) -> str:
        """ Mimic one remote backend that prepends the configured location.

        Args:
            filename: Relative generated filename.

        Returns:
            str: Location-prefixed generated filename.
        """
        return f"{self.location}/{filename.lstrip('/')}"


class FakeRemoteTenantMediaStorage(TenantAwareMediaStorageMixin, FakeRemoteMediaStorageBase):
    """ Compose the tenant-aware mixin with one fake remote storage backend. """


class TestTenantMediaStorage(LoggedSimpleTestCase):
    """ Verify media storage prefixes uploaded files with the active tenant. """

    base_dir: Path

    @classmethod
    def setUpClass(cls) -> None:
        """ Prepare a stable base directory for storage adapter resolution. """
        super().setUpClass()
        cls.base_dir = Path(__file__).resolve().parents[4]

    def test_build_tenant_media_name_keeps_names_unchanged_without_an_active_tenant(self) -> None:
        """ Verify media object names stay untouched when no tenant context exists. """
        self.assertEqual("products/image.png", TenantMediaPathBuilder.build_tenant_media_name("products/image.png"))

    def test_build_tenant_media_name_prefixes_names_with_the_active_tenant_slug(self) -> None:
        """ Verify media object names gain the active tenant folder when a tenant is present. """
        tenant = TenantModel(name="GEA Center", slug="gea-center")
        tenant_token = ActiveTenantContext.set(tenant)

        try:
            self.assertEqual(
                "tenants/gea-center/products/image.png",
                TenantMediaPathBuilder.build_tenant_media_name("products/image.png"),
            )
        finally:
            ActiveTenantContext.reset(tenant_token)

    def test_tenant_file_system_storage_saves_generated_names_inside_the_active_tenant_folder(self) -> None:
        """ Verify local storage saves tenant-prefixed names returned by generate_filename. """
        tenant = TenantModel(name="GEA Center", slug="gea-center")
        tenant_token = ActiveTenantContext.set(tenant)

        try:
            with TemporaryDirectory() as media_root:
                storage = TenantFileSystemStorage(location=media_root, base_url="/media/")
                generated_name = storage.generate_filename("products/image.txt")
                stored_name = storage.save(generated_name, ContentFile(b"hello"))

                self.assertEqual(
                    "tenants/gea-center/products/image.txt",
                    Path(generated_name).as_posix(),
                )
                self.assertEqual(
                    "tenants/gea-center/products/image.txt",
                    Path(stored_name).as_posix(),
                )
                self.assertTrue(Path(media_root, stored_name).exists())
        finally:
            ActiveTenantContext.reset(tenant_token)

    def test_media_storage_resolver_build_config_uses_the_tenant_aware_local_backend(self) -> None:
        """ Verify local media configuration now uses the tenant-aware filesystem backend. """
        environment = {
            "MEDIAFILES_PROVIDER": "local",
            "MEDIA_URL": "/media/",
            "MEDIA_ROOT": "media",
        }

        with (
            patch.dict(os.environ, environment, clear=False),
            patch("core.config.storage.media_storage.media_storage_adapter_resolver.logger.info") as logger_info_mock,
        ):
            storage_config = MediaStorageAdapterResolver.build_config(self.base_dir)

        self.assertEqual(
            "core.config.storage.media_storage.backends.tenant_file_system_storage.TenantFileSystemStorage",
            storage_config.storages["default"]["BACKEND"],
        )
        logger_info_mock.assert_called_once()

    def test_remote_generate_filename_applies_tenant_prefix_behind_location_once(self) -> None:
        """ Verify remote generated names keep one tenant prefix behind the storage location. """
        tenant = TenantModel(name="GEA Trader", slug="gea-trader")
        tenant_token = ActiveTenantContext.set(tenant)

        try:
            storage = FakeRemoteTenantMediaStorage()
            generated_name = storage.generate_filename("branding/logos/logo.png")
            saved_name = storage.save(generated_name, ContentFile(b"logo"))

            self.assertEqual(
                "media/tenants/gea-trader/branding/logos/logo.png",
                generated_name,
            )
            self.assertEqual(
                "media/tenants/gea-trader/branding/logos/logo.png",
                saved_name,
            )
        finally:
            ActiveTenantContext.reset(tenant_token)
