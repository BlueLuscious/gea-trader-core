""" Unit tests for the S3 storage adapter. """

import os
from pathlib import Path
from unittest.mock import patch
from core.config.storage import build_media_storage_config
from core.config.storage.media_storage.s3 import S3MediaStorageAdapter
from core.testing.base import LoggedSimpleTestCase


class TestS3StorageAdapter(LoggedSimpleTestCase):
    """ Cover S3 adapter configuration behavior without remote I/O. """

    base_dir: Path

    @classmethod
    def setUpClass(cls) -> None:
        """ Prepare a stable base directory for adapter resolution. """
        super().setUpClass()
        cls.base_dir = Path(__file__).resolve().parents[4]

    def build_environment(self, **overrides: str) -> dict[str, str]:
        """ Build an environment dictionary for the S3 adapter.

        Args:
            **overrides: Environment overrides applied on top of the defaults.

        Returns:
            dict[str, str]: Complete environment mapping for adapter tests.
        """
        environment = {
            "MEDIAFILES_PROVIDER": "s3",
            "MEDIAFILES_LOCATION": "media",
            "MEDIA_URL": "/media/",
            "MEDIA_ROOT": "media",
            "AWS_STORAGE_BUCKET_NAME": "gea-trader",
            "AWS_ACCESS_KEY_ID": "access-key",
            "AWS_SECRET_ACCESS_KEY": "secret-key",
            "AWS_S3_REGION_NAME": "us-east-1",
            "AWS_S3_ENDPOINT_URL": "https://s3.amazonaws.com",
            "AWS_S3_CUSTOM_DOMAIN": "",
            "AWS_DEFAULT_ACL": "",
            "AWS_S3_FILE_OVERWRITE": "False",
            "AWS_QUERYSTRING_AUTH": "True",
            "AWS_S3_SIGNATURE_VERSION": "s3v4",
            "AWS_S3_ADDRESSING_STYLE": "virtual",
        }
        environment.update(overrides)
        return environment

    def test_s3_storage_adapter__build_media_storage_config_keeps_explicit_endpoint(self) -> None:
        """ Verify the S3 adapter keeps the configured endpoint inside media storage options. """
        with patch.dict(os.environ, self.build_environment(), clear=False):
            storage_config = build_media_storage_config(self.base_dir)

        self.assertEqual(storage_config.provider, "s3")
        self.assertEqual(storage_config.storages["default"]["BACKEND"], "storages.backends.s3.S3Storage")
        self.assertEqual(
            storage_config.storages["default"]["OPTIONS"]["endpoint_url"],
            "https://s3.amazonaws.com",
        )

    def test_s3_storage_adapter__custom_domain_builds_media_url_with_media_location(self) -> None:
        """ Verify the S3 adapter builds a public media URL from the custom domain and media location. """
        with patch.dict(
            os.environ,
            self.build_environment(
                AWS_S3_CUSTOM_DOMAIN="cdn.example.com",
                MEDIAFILES_LOCATION="assets-media",
            ),
            clear=False,
        ):
            storage_config = build_media_storage_config(self.base_dir)

        self.assertEqual(storage_config.media_url, "https://cdn.example.com/assets-media/")

    def test_s3_storage_adapter__storage_options_keep_expected_s3_flags(self) -> None:
        """ Verify the S3 adapter preserves the expected bucket, signature and overwrite options. """
        with patch.dict(
            os.environ,
            self.build_environment(
                AWS_S3_FILE_OVERWRITE="True",
                AWS_QUERYSTRING_AUTH="False",
            ),
            clear=False,
        ):
            adapter = S3MediaStorageAdapter()
            options = adapter.build_storage_options()

        self.assertEqual(options["bucket_name"], "gea-trader")
        self.assertEqual(options["region_name"], "us-east-1")
        self.assertEqual(options["signature_version"], "s3v4")
        self.assertEqual(options["addressing_style"], "virtual")
        self.assertTrue(bool(options["file_overwrite"]))
        self.assertFalse(bool(options["querystring_auth"]))

    def test_s3_storage_adapter__default_media_url_falls_back_to_media_url_env(self) -> None:
        """ Verify the S3 adapter falls back to MEDIA_URL when no custom domain is configured. """
        with patch.dict(os.environ, self.build_environment(MEDIA_URL="/custom-media/"), clear=False):
            adapter = S3MediaStorageAdapter()
            media_url = adapter.build_media_url()

        self.assertEqual(media_url, "/custom-media/")
