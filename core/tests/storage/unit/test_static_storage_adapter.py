""" Unit tests for static storage adapters. """

import os
from pathlib import Path
from unittest.mock import patch
from core.config.storage import StaticStorageAdapterResolver
from core.config.storage.static_storage.adapters import WhiteNoiseStaticStorageAdapter
from core.testing.base import LoggedSimpleTestCase


class TestStaticStorageAdapter(LoggedSimpleTestCase):
    """ Cover static storage adapter discovery and static-specific behavior. """

    base_dir: Path

    @classmethod
    def setUpClass(cls) -> None:
        """ Prepare a stable base directory for adapter resolution. """
        super().setUpClass()
        cls.base_dir = Path(__file__).resolve().parents[4]

    def build_environment(self, **overrides: str) -> dict[str, str]:
        """ Build an environment dictionary for static storage adapter tests.

        Args:
            **overrides: Environment overrides applied on top of the defaults.

        Returns:
            dict[str, str]: Complete environment mapping for static adapter tests.
        """
        environment = {
            "STATICFILES_PROVIDER": "local",
            "STATIC_URL": "/static/",
            "STATIC_ROOT": "staticfiles",
            "STATICFILES_LOCATION": "static",
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

    def test_static_storage_adapter__resolver_build_config_uses_local_backend(self) -> None:
        """ Verify the local static adapter builds Django staticfiles storage without extra middleware. """
        with (
            patch.dict(os.environ, self.build_environment(), clear=False),
            patch("core.config.storage.static_storage.static_storage_adapter_resolver.logger.info") as logger_info_mock,
        ):
            static_storage_config = StaticStorageAdapterResolver.build_config(self.base_dir)

        self.assertEqual(static_storage_config.provider, "local")
        self.assertEqual(
            static_storage_config.storages["staticfiles"]["BACKEND"],
            "django.contrib.staticfiles.storage.StaticFilesStorage",
        )
        self.assertEqual(static_storage_config.extra_middleware, [])
        logger_info_mock.assert_called_once()

    def test_static_storage_adapter__whitenoise_adds_expected_middleware(self) -> None:
        """ Verify the WhiteNoise adapter adds the expected middleware and backend. """
        with patch("importlib.util.find_spec", return_value=object()):
            with patch.dict(os.environ, self.build_environment(STATICFILES_PROVIDER="whitenoise"), clear=False):
                static_storage_config = StaticStorageAdapterResolver.build_config(self.base_dir)

        self.assertEqual(static_storage_config.provider, "whitenoise")
        self.assertEqual(
            static_storage_config.storages["staticfiles"]["BACKEND"],
            "whitenoise.storage.CompressedManifestStaticFilesStorage",
        )
        self.assertEqual(static_storage_config.extra_middleware, ["whitenoise.middleware.WhiteNoiseMiddleware"])

    def test_static_storage_adapter__s3_builds_custom_domain_url_with_location(self) -> None:
        """ Verify the S3 static adapter builds a public static URL from custom domain and location. """
        with patch.dict(
            os.environ,
            self.build_environment(
                STATICFILES_PROVIDER="s3",
                AWS_S3_CUSTOM_DOMAIN="cdn.example.com",
                STATICFILES_LOCATION="assets-static",
            ),
            clear=False,
        ):
            static_storage_config = StaticStorageAdapterResolver.build_config(self.base_dir)

        self.assertEqual(static_storage_config.static_url, "https://cdn.example.com/assets-static/")

    def test_static_storage_adapter__whitenoise_raises_when_dependency_is_missing(self) -> None:
        """ Verify the WhiteNoise adapter fails clearly when the dependency is unavailable. """
        with patch("importlib.util.find_spec", return_value=None):
            with self.assertRaises(RuntimeError):
                WhiteNoiseStaticStorageAdapter().ensure_dependencies()
