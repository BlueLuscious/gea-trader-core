""" Object-oriented resolver for static storage adapters and configuration. """

import logging, os
from pathlib import Path
from core.config.storage.static_storage.adapters import (
    BaseStaticStorageAdapter,
    LocalStaticStorageAdapter,
    R2StaticStorageAdapter,
    S3StaticStorageAdapter,
    StaticStorageConfig,
    WhiteNoiseStaticStorageAdapter,
)

logger = logging.getLogger(__name__)


class StaticStorageAdapterResolver:
    """ Resolve static storage adapters and build provider-specific configuration."""

    adapter_classes: dict[str, type[BaseStaticStorageAdapter]] = {
        "local": LocalStaticStorageAdapter,
        "whitenoise": WhiteNoiseStaticStorageAdapter,
        "s3": S3StaticStorageAdapter,
        "r2": R2StaticStorageAdapter,
    }

    @classmethod
    def get_adapter(cls, provider: str) -> BaseStaticStorageAdapter:
        """ Resolve the adapter for one static storage provider.

        Args:
            provider: Static storage provider identifier from environment.

        Returns:
            BaseStaticStorageAdapter: Adapter responsible for the requested provider.
        """
        try:
            adapter_class = cls.adapter_classes[provider]
        except KeyError as exc:
            raise ValueError("STATICFILES_PROVIDER must be one of: local, whitenoise, s3, r2.") from exc

        return adapter_class()

    @classmethod
    def build_config(cls, base_dir: Path) -> StaticStorageConfig:
        """ Build static storage settings from environment variables.

        Args:
            base_dir: Project base directory used to resolve local paths.

        Returns:
            StaticStorageConfig: Resolved static storage configuration for the active provider.
        """
        provider = os.environ.get("STATICFILES_PROVIDER", "local").lower()
        storage_config = cls.get_adapter(provider).build(base_dir)
        logger.info(
            "Resolved static storage provider=%s backend=%s extra_apps=%s extra_middleware=%s",
            storage_config.provider,
            storage_config.storages["staticfiles"]["BACKEND"],
            storage_config.extra_apps,
            storage_config.extra_middleware,
        )
        return storage_config
