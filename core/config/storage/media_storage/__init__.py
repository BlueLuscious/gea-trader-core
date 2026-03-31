""" Public media storage configuration API. """

import os
from pathlib import Path
from core.config.storage.media_storage.base_media_storage_adapter import BaseMediaStorageAdapter, MediaStorageConfig
from core.config.storage.media_storage.local import LocalMediaStorageAdapter
from core.config.storage.media_storage.r2 import R2MediaStorageAdapter
from core.config.storage.media_storage.s3 import S3MediaStorageAdapter


def get_media_storage_adapter(provider: str) -> BaseMediaStorageAdapter:
    """ Resolve the media storage adapter for the requested provider.

    Args:
        provider: Media storage provider identifier from environment.

    Returns:
        BaseMediaStorageAdapter: Adapter responsible for the requested provider.
    """
    adapters: dict[str, BaseMediaStorageAdapter] = {
        "local": LocalMediaStorageAdapter(),
        "s3": S3MediaStorageAdapter(),
        "r2": R2MediaStorageAdapter(),
    }

    try:
        return adapters[provider]
    except KeyError as exc:
        raise ValueError("MEDIAFILES_PROVIDER must be one of: local, s3, r2.") from exc


def build_media_storage_config(base_dir: Path) -> MediaStorageConfig:
    """ Build media storage settings from environment variables.

    Args:
        base_dir: Project base directory used to resolve local media paths.

    Returns:
        MediaStorageConfig: Resolved media storage configuration for the active provider.
    """
    provider = os.environ.get("MEDIAFILES_PROVIDER", "local").lower()
    adapter = get_media_storage_adapter(provider)
    return adapter.build(base_dir)


__all__ = [
    "BaseMediaStorageAdapter",
    "MediaStorageConfig",
    "LocalMediaStorageAdapter",
    "S3MediaStorageAdapter",
    "R2MediaStorageAdapter",
    "get_media_storage_adapter",
    "build_media_storage_config",
]
