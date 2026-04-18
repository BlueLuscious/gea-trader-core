""" Static storage adapters grouped by provider. """

from .base_static_storage_adapter import BaseStaticStorageAdapter
from .base_static_storage_adapter import StaticStorageConfig
from .local_static_storage_adapter import LocalStaticStorageAdapter
from .r2_static_storage_adapter import R2StaticStorageAdapter
from .s3_static_storage_adapter import S3StaticStorageAdapter
from .whitenoise import WhiteNoiseStaticStorageAdapter

__all__: list[str] = [
    "BaseStaticStorageAdapter",
    "StaticStorageConfig",
    "LocalStaticStorageAdapter",
    "R2StaticStorageAdapter",
    "S3StaticStorageAdapter",
    "WhiteNoiseStaticStorageAdapter",
]
