""" Public static storage configuration API. """

from core.config.storage.static_storage.adapters import (
    BaseStaticStorageAdapter,
    LocalStaticStorageAdapter,
    R2StaticStorageAdapter,
    S3StaticStorageAdapter,
    StaticStorageConfig,
    WhiteNoiseStaticStorageAdapter,
)
from core.config.storage.static_storage.static_storage_adapter_resolver import StaticStorageAdapterResolver


__all__ = [
    "BaseStaticStorageAdapter",
    "StaticStorageConfig",
    "LocalStaticStorageAdapter",
    "WhiteNoiseStaticStorageAdapter",
    "S3StaticStorageAdapter",
    "R2StaticStorageAdapter",
    "StaticStorageAdapterResolver",
]
