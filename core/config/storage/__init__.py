""" Public storage configuration API for media and static storage. """

from core.config.storage.common import (
    build_extra_apps,
    build_remote_url,
    build_s3_compatible_storage_options,
    normalize_location, parse_bool_env
)
from core.config.storage.media_storage import (
    BaseMediaStorageAdapter,
    MediaStorageConfig,
    build_media_storage_config,
    get_media_storage_adapter
)
from core.config.storage.static_storage import (
    BaseStaticStorageAdapter,
    StaticStorageConfig,
    build_static_storage_config,
    get_static_storage_adapter
)

__all__ = [
    "BaseMediaStorageAdapter",
    "MediaStorageConfig",
    "BaseStaticStorageAdapter",
    "StaticStorageConfig",
    "build_extra_apps",
    "build_remote_url",
    "build_s3_compatible_storage_options",
    "normalize_location",
    "parse_bool_env",
    "get_media_storage_adapter",
    "build_media_storage_config",
    "get_static_storage_adapter",
    "build_static_storage_config",
]
