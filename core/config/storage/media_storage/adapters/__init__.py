""" Media storage adapters grouped by provider. """

from .base_media_storage_adapter import BaseMediaStorageAdapter
from .base_media_storage_adapter import MediaStorageConfig
from .local_media_storage_adapter import LocalMediaStorageAdapter
from .r2_media_storage_adapter import R2MediaStorageAdapter
from .s3_media_storage_adapter import S3MediaStorageAdapter

__all__: list[str] = [
    "BaseMediaStorageAdapter",
    "MediaStorageConfig",
    "LocalMediaStorageAdapter",
    "R2MediaStorageAdapter",
    "S3MediaStorageAdapter",
]
