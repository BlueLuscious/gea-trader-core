""" Amazon S3 compatible media storage adapter. """

import os
from pathlib import Path
from typing import Any
from core.config.storage.common import build_extra_apps, build_remote_url, build_s3_compatible_storage_options, normalize_location
from core.config.storage.media_storage.adapters.base_media_storage_adapter import BaseMediaStorageAdapter, MediaStorageConfig


class S3MediaStorageAdapter(BaseMediaStorageAdapter):
    """ Build media storage settings for Amazon S3 compatible backends. """

    provider = "s3"

    def build(self, base_dir: Path) -> MediaStorageConfig:
        """ Build S3 media storage configuration.

        Args:
            base_dir: Project base directory used to resolve local paths.

        Returns:
            MediaStorageConfig: S3 media storage configuration.
        """
        self.ensure_dependencies()

        return MediaStorageConfig(
            provider=self.provider,
            media_url=self.build_media_url(),
            media_root=self.get_media_root(base_dir),
            storages={
                "default": {
                    "BACKEND": "core.config.storage.media_storage.backends.tenant_s3_storage.TenantS3Storage",
                    "OPTIONS": self.build_storage_options(),
                },
            },
            extra_apps=build_extra_apps(),
        )

    def ensure_dependencies(self) -> None:
        """ Ensure required third-party dependencies are available. """
        if "storages" not in build_extra_apps():
            raise RuntimeError("Remote file storage requires django-storages to be installed.")

    def build_media_url(self) -> str:
        """ Resolve the media URL for the remote provider.

        Returns:
            str: Remote or fallback media URL.
        """
        location = normalize_location("MEDIAFILES_LOCATION", "media")
        return build_remote_url(
            custom_domain=os.environ.get("AWS_S3_CUSTOM_DOMAIN", ""),
            location=location,
            fallback_url=self.get_media_url(),
        )

    def build_storage_options(self) -> dict[str, Any]:
        """ Build common S3 media storage options from environment variables.

        Returns:
            dict[str, Any]: Keyword arguments for the S3 media storage backend.
        """
        return build_s3_compatible_storage_options(
            location_env_name="MEDIAFILES_LOCATION",
            default_location="media",
            default_file_overwrite=False,
            default_querystring_auth=True,
        )
