""" Shared helpers for media and static storage adapters. """

import importlib.util, os
from typing import Any


def build_extra_apps() -> list[str]:
    """ Resolve extra Django apps required by storage providers.

    Returns:
        list[str]: Additional installed apps for the current provider.
    """
    return ["storages"] if importlib.util.find_spec("storages") is not None else []


def parse_bool_env(name: str, default: bool) -> bool:
    """ Parse a boolean environment variable using Django-style truthy values.

    Args:
        name: Environment variable name to inspect.
        default: Default value used when the variable is missing.

    Returns:
        bool: Parsed boolean value.
    """
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    return raw_value.lower() in ("1", "true", "yes", "on")


def normalize_location(name: str, default: str) -> str:
    """ Normalize a bucket location prefix from environment.

    Args:
        name: Environment variable holding the logical prefix.
        default: Fallback prefix used when the env var is empty or missing.

    Returns:
        str: Normalized storage prefix without leading or trailing slashes.
    """
    return os.environ.get(name, default).strip().strip("/") or default


def build_remote_url(custom_domain: str, location: str, fallback_url: str) -> str:
    """ Build a public URL for remote storage when a custom domain is configured.

    Args:
        custom_domain: Optional CDN or bucket custom domain.
        location: Logical prefix inside the remote bucket.
        fallback_url: URL returned when no custom domain is configured.

    Returns:
        str: Public URL for the remote prefix or the fallback URL.
    """
    normalized_domain = custom_domain.strip()
    if not normalized_domain:
        return fallback_url
    return f"https://{normalized_domain.rstrip('/')}/{location}/"


def build_s3_compatible_storage_options(
    *,
    location_env_name: str,
    default_location: str,
    default_file_overwrite: bool,
    default_querystring_auth: bool,
) -> dict[str, Any]:
    """ Build shared S3-compatible storage options from environment variables.

    Args:
        location_env_name: Environment variable name used for the storage prefix.
        default_location: Fallback storage prefix.
        default_file_overwrite: Default file overwrite behavior for the backend.
        default_querystring_auth: Default querystring auth behavior for the backend.

    Returns:
        dict[str, Any]: Keyword arguments for S3-compatible backends.
    """
    return {
        "bucket_name": os.environ.get("AWS_STORAGE_BUCKET_NAME", ""),
        "access_key": os.environ.get("AWS_ACCESS_KEY_ID", ""),
        "secret_key": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        "region_name": os.environ.get("AWS_S3_REGION_NAME", ""),
        "endpoint_url": os.environ.get("AWS_S3_ENDPOINT_URL", ""),
        "custom_domain": os.environ.get("AWS_S3_CUSTOM_DOMAIN", ""),
        "location": normalize_location(location_env_name, default_location),
        "default_acl": os.environ.get("AWS_DEFAULT_ACL") or None,
        "file_overwrite": parse_bool_env("AWS_S3_FILE_OVERWRITE", default_file_overwrite),
        "querystring_auth": parse_bool_env("AWS_QUERYSTRING_AUTH", default_querystring_auth),
        "signature_version": os.environ.get("AWS_S3_SIGNATURE_VERSION") or None,
        "addressing_style": os.environ.get("AWS_S3_ADDRESSING_STYLE") or None,
    }
