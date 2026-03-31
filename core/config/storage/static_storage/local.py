""" Local filesystem static storage adapter. """

from pathlib import Path
from core.config.storage.static_storage.base_static_storage_adapter import BaseStaticStorageAdapter, StaticStorageConfig


class LocalStaticStorageAdapter(BaseStaticStorageAdapter):
    """ Build static storage settings for local filesystem usage. """

    provider = "local"

    def build(self, base_dir: Path) -> StaticStorageConfig:
        """ Build local static storage configuration.

        Args:
            base_dir: Project base directory used to resolve local paths.

        Returns:
            StaticStorageConfig: Local static storage configuration.
        """
        return StaticStorageConfig(
            provider=self.provider,
            static_url=self.get_static_url(),
            static_root=self.get_static_root(base_dir),
            storages={
                "staticfiles": {
                    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
                    "OPTIONS": {},
                },
            },
            extra_apps=[],
            extra_middleware=[],
        )
