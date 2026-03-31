""" Unit tests for the Cloudflare R2 storage adapter. """

import os
from pathlib import Path
from unittest.mock import patch
from core.config.storage import build_media_storage_config
from core.config.storage.media_storage.r2 import R2MediaStorageAdapter
from core.testing.base import LoggedSimpleTestCase


class TestR2StorageAdapter(LoggedSimpleTestCase):
    """ Cover R2 adapter configuration behavior without remote I/O. """

    base_dir: Path

    @classmethod
    def setUpClass(cls) -> None:
        """ Prepare a stable base directory for adapter resolution. """
        super().setUpClass()
        cls.base_dir = Path(__file__).resolve().parents[4]

    def build_environment(self, **overrides: str) -> dict[str, str]:
        """ Build an environment dictionary for the R2 adapter.

        Args:
            **overrides: Environment overrides applied on top of the defaults.

        Returns:
            dict[str, str]: Complete environment mapping for adapter tests.
        """
        environment = {
            "MEDIAFILES_PROVIDER": "r2",
            "MEDIAFILES_LOCATION": "media",
            "MEDIA_URL": "/media/",
            "MEDIA_ROOT": "media",
            "AWS_STORAGE_BUCKET_NAME": "gea-trader",
            "AWS_ACCESS_KEY_ID": "access-key",
            "AWS_SECRET_ACCESS_KEY": "secret-key",
            "AWS_S3_REGION_NAME": "auto",
            "AWS_S3_ENDPOINT_URL": "",
            "AWS_S3_CUSTOM_DOMAIN": "",
            "AWS_DEFAULT_ACL": "",
            "AWS_S3_FILE_OVERWRITE": "False",
            "AWS_QUERYSTRING_AUTH": "True",
            "AWS_S3_SIGNATURE_VERSION": "s3v4",
            "AWS_S3_ADDRESSING_STYLE": "virtual",
            "CLOUDFLARE_R2_ACCOUNT_ID": "account-123",
        }
        environment.update(overrides)
        return environment

    def test_r2_storage_adapter__build_media_storage_config_derives_endpoint_from_account_id(self) -> None:
        """ Verify the R2 adapter derives the endpoint when no explicit endpoint is configured. """
        with patch.dict(os.environ, self.build_environment(), clear=False):
            storage_config = build_media_storage_config(self.base_dir)

        self.assertEqual(storage_config.provider, "r2")
        self.assertEqual(storage_config.storages["default"]["BACKEND"], "storages.backends.s3.S3Storage")
        self.assertEqual(
            storage_config.storages["default"]["OPTIONS"]["endpoint_url"],
            "https://account-123.r2.cloudflarestorage.com",
        )

    def test_r2_storage_adapter__explicit_endpoint_takes_precedence_over_account_id(self) -> None:
        """ Verify the R2 adapter preserves an explicit endpoint instead of deriving one. """
        with patch.dict(
            os.environ,
            self.build_environment(
                AWS_S3_ENDPOINT_URL="https://custom-endpoint.example.com",
                CLOUDFLARE_R2_ACCOUNT_ID="account-456",
            ),
            clear=False,
        ):
            adapter = R2MediaStorageAdapter()
            options = adapter.build_storage_options()

        self.assertEqual(options["endpoint_url"], "https://custom-endpoint.example.com")

    def test_r2_storage_adapter__custom_domain_builds_media_url_with_media_location(self) -> None:
        """ Verify the R2 adapter builds a public media URL from the custom domain and media location. """
        with patch.dict(
            os.environ,
            self.build_environment(
                AWS_S3_CUSTOM_DOMAIN="cdn.example.com",
                MEDIAFILES_LOCATION="product-media",
            ),
            clear=False,
        ):
            storage_config = build_media_storage_config(self.base_dir)

        self.assertEqual(storage_config.media_url, "https://cdn.example.com/product-media/")

    def test_r2_storage_adapter__storage_options_keep_expected_s3_compatibility_flags(self) -> None:
        """ Verify the R2 adapter keeps the expected S3 compatibility options for django-storages. """
        with patch.dict(os.environ, self.build_environment(AWS_S3_ADDRESSING_STYLE="path"), clear=False):
            adapter = R2MediaStorageAdapter()
            options = adapter.build_storage_options()

        self.assertEqual(options["bucket_name"], "gea-trader")
        self.assertEqual(options["region_name"], "auto")
        self.assertEqual(options["signature_version"], "s3v4")
        self.assertEqual(options["addressing_style"], "path")
        self.assertFalse(bool(options["file_overwrite"]))
        self.assertTrue(bool(options["querystring_auth"]))
