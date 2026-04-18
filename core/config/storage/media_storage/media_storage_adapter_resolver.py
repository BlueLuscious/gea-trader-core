""" Object-oriented resolver for media storage adapters and configuration. """

import logging, os
from pathlib import Path
from core.config.storage.media_storage.adapters import (
    BaseMediaStorageAdapter,
    LocalMediaStorageAdapter,
    MediaStorageConfig,
    R2MediaStorageAdapter,
    S3MediaStorageAdapter,
)

logger = logging.getLogger(__name__)


class MediaStorageAdapterResolver:
    """ Resolve media storage adapters and build provider-specific configuration. """

    adapter_classes: dict[str, type[BaseMediaStorageAdapter]] = {
        "local": LocalMediaStorageAdapter,
        "s3": S3MediaStorageAdapter,
        "r2": R2MediaStorageAdapter,
    }

    @classmethod
    def get_adapter(cls, provider: str) -> BaseMediaStorageAdapter:
        """ Resolve the adapter for one media storage provider.

        Args:
            provider: Media storage provider identifier from environment.

        Returns:
            BaseMediaStorageAdapter: Adapter responsible for the requested provider.
        """
        try:
            adapter_class = cls.adapter_classes[provider]
        except KeyError as exc:
            raise ValueError("MEDIAFILES_PROVIDER must be one of: local, s3, r2.") from exc

        return adapter_class()

    @classmethod
    def build_config(cls, base_dir: Path) -> MediaStorageConfig:
        """ Build media storage settings from environment variables.

        Args:
            base_dir: Project base directory used to resolve local media paths.

        Returns:
            MediaStorageConfig: Resolved media storage configuration for the active provider.
        """
        provider = os.environ.get("MEDIAFILES_PROVIDER", "local").lower()
        storage_config = cls.get_adapter(provider).build(base_dir)
        logger.info(
            "Resolved media storage provider=%s backend=%s extra_apps=%s",
            storage_config.provider,
            storage_config.storages["default"]["BACKEND"],
            storage_config.extra_apps,
        )
        return storage_config
