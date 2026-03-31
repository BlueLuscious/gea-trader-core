""" WhiteNoise static storage adapter. """

import importlib.util
from pathlib import Path
from core.config.storage.static_storage.base_static_storage_adapter import BaseStaticStorageAdapter, StaticStorageConfig


class WhiteNoiseStaticStorageAdapter(BaseStaticStorageAdapter):
    """ Build static storage settings for WhiteNoise-backed deployments. """

    provider = "whitenoise"

    def build(self, base_dir: Path) -> StaticStorageConfig:
        """ Build WhiteNoise static storage configuration.

        Args:
            base_dir: Project base directory used to resolve local paths.

        Returns:
            StaticStorageConfig: WhiteNoise static storage configuration.
        """
        self.ensure_dependencies()

        return StaticStorageConfig(
            provider=self.provider,
            static_url=self.get_static_url(),
            static_root=self.get_static_root(base_dir),
            storages={
                "staticfiles": {
                    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
                    "OPTIONS": {},
                },
            },
            extra_apps=[],
            extra_middleware=["whitenoise.middleware.WhiteNoiseMiddleware"],
        )

    def ensure_dependencies(self) -> None:
        """ Ensure WhiteNoise is available before using this provider. """
        if importlib.util.find_spec("whitenoise") is None:
            raise RuntimeError("STATICFILES_PROVIDER=whitenoise requires whitenoise to be installed.")
