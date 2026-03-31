""" Amazon S3 compatible static storage adapter. """

import os
from pathlib import Path
from core.config.storage.common import build_extra_apps, build_remote_url, build_s3_compatible_storage_options, normalize_location
from core.config.storage.static_storage.base_static_storage_adapter import BaseStaticStorageAdapter, StaticStorageConfig


class S3StaticStorageAdapter(BaseStaticStorageAdapter):
    """ Build static storage settings for Amazon S3 compatible backends. """

    provider = "s3"

    def build(self, base_dir: Path) -> StaticStorageConfig:
        """ Build S3 static storage configuration.

        Args:
            base_dir: Project base directory used to resolve local paths.

        Returns:
            StaticStorageConfig: S3 static storage configuration.
        """
        self.ensure_dependencies()

        return StaticStorageConfig(
            provider=self.provider,
            static_url=self.build_static_url(),
            static_root=self.get_static_root(base_dir),
            storages={
                "staticfiles": {
                    "BACKEND": "storages.backends.s3.S3Storage",
                    "OPTIONS": self.build_storage_options(),
                },
            },
            extra_apps=build_extra_apps(),
            extra_middleware=[],
        )

    def ensure_dependencies(self) -> None:
        """ Ensure required third-party dependencies are available. """
        if "storages" not in build_extra_apps():
            raise RuntimeError("Remote staticfiles storage requires django-storages to be installed.")

    def build_static_url(self) -> str:
        """ Resolve the static URL for the remote provider.

        Returns:
            str: Remote or fallback static URL.
        """
        location = normalize_location("STATICFILES_LOCATION", "static")
        return build_remote_url(
            custom_domain=os.environ.get("AWS_S3_CUSTOM_DOMAIN", ""),
            location=location,
            fallback_url=self.get_static_url(),
        )

    def build_storage_options(self) -> dict[str, object]:
        """ Build common S3 static storage options from environment variables.

        Returns:
            dict[str, object]: Keyword arguments for the S3 static storage backend.
        """
        return build_s3_compatible_storage_options(
            location_env_name="STATICFILES_LOCATION",
            default_location="static",
            default_file_overwrite=True,
            default_querystring_auth=False,
        )
