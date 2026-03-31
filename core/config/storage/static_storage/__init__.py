""" Public static storage configuration API. """

import os
from pathlib import Path
from core.config.storage.static_storage.base_static_storage_adapter import BaseStaticStorageAdapter, StaticStorageConfig
from core.config.storage.static_storage.local import LocalStaticStorageAdapter
from core.config.storage.static_storage.r2 import R2StaticStorageAdapter
from core.config.storage.static_storage.s3 import S3StaticStorageAdapter
from core.config.storage.static_storage.whitenoise import WhiteNoiseStaticStorageAdapter


def get_static_storage_adapter(provider: str) -> BaseStaticStorageAdapter:
    """ Resolve the static storage adapter for the requested provider.

    Args:
        provider: Static storage provider identifier from environment.

    Returns:
        BaseStaticStorageAdapter: Adapter responsible for the requested provider.
    """
    adapters: dict[str, BaseStaticStorageAdapter] = {
        "local": LocalStaticStorageAdapter(),
        "whitenoise": WhiteNoiseStaticStorageAdapter(),
        "s3": S3StaticStorageAdapter(),
        "r2": R2StaticStorageAdapter(),
    }

    try:
        return adapters[provider]
    except KeyError as exc:
        raise ValueError("STATICFILES_PROVIDER must be one of: local, whitenoise, s3, r2.") from exc


def build_static_storage_config(base_dir: Path) -> StaticStorageConfig:
    """ Build static storage settings from environment variables.

    Args:
        base_dir: Project base directory used to resolve local paths.

    Returns:
        StaticStorageConfig: Resolved static storage configuration for the active provider.
    """
    provider = os.environ.get("STATICFILES_PROVIDER", "local").lower()
    adapter = get_static_storage_adapter(provider)
    return adapter.build(base_dir)


__all__ = [
    "BaseStaticStorageAdapter",
    "StaticStorageConfig",
    "LocalStaticStorageAdapter",
    "WhiteNoiseStaticStorageAdapter",
    "S3StaticStorageAdapter",
    "R2StaticStorageAdapter",
    "get_static_storage_adapter",
    "build_static_storage_config",
]
