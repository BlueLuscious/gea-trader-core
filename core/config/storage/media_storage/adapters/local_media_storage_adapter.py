""" Local filesystem media storage adapter. """

from pathlib import Path
from core.config.storage.common import build_extra_apps
from core.config.storage.media_storage.adapters.base_media_storage_adapter import BaseMediaStorageAdapter, MediaStorageConfig


class LocalMediaStorageAdapter(BaseMediaStorageAdapter):
    """ Build media storage settings for local filesystem usage. """

    provider = "local"

    def build(self, base_dir: Path) -> MediaStorageConfig:
        """ Build local filesystem media storage configuration.

        Args:
            base_dir: Project base directory used to resolve local paths.

        Returns:
            MediaStorageConfig: Local media storage configuration.
        """
        return MediaStorageConfig(
            provider=self.provider,
            media_url=self.get_media_url(),
            media_root=self.get_media_root(base_dir),
            storages={
                "default": {
                    "BACKEND": "core.config.storage.media_storage.backends.tenant_file_system_storage.TenantFileSystemStorage",
                    "OPTIONS": {},
                },
            },
            extra_apps=build_extra_apps(),
        )
