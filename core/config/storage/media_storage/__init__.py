""" Public media storage configuration API. """

from core.config.storage.media_storage.adapters import (
    BaseMediaStorageAdapter,
    LocalMediaStorageAdapter,
    MediaStorageConfig,
    R2MediaStorageAdapter,
    S3MediaStorageAdapter,
)
from core.config.storage.media_storage.media_storage_adapter_resolver import MediaStorageAdapterResolver


__all__ = [
    "BaseMediaStorageAdapter",
    "MediaStorageConfig",
    "LocalMediaStorageAdapter",
    "S3MediaStorageAdapter",
    "R2MediaStorageAdapter",
    "MediaStorageAdapterResolver",
]
