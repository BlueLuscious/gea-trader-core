""" Public storage configuration API for media and static storage. """

from core.config.storage.common import (
    build_extra_apps,
    build_remote_url,
    build_s3_compatible_storage_options,
    normalize_location, parse_bool_env
)
from core.config.storage.media_storage import (
    BaseMediaStorageAdapter,
    MediaStorageAdapterResolver,
    MediaStorageConfig,
)
from core.config.storage.static_storage import (
    BaseStaticStorageAdapter,
    StaticStorageAdapterResolver,
    StaticStorageConfig,
)

__all__ = [
    "BaseMediaStorageAdapter",
    "MediaStorageAdapterResolver",
    "MediaStorageConfig",
    "BaseStaticStorageAdapter",
    "StaticStorageAdapterResolver",
    "StaticStorageConfig",
    "build_extra_apps",
    "build_remote_url",
    "build_s3_compatible_storage_options",
    "normalize_location",
    "parse_bool_env",
]
