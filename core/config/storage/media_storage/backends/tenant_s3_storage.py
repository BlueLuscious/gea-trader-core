""" S3-compatible media backend with tenant-aware path prefixing. """

from storages.backends.s3 import S3Storage
from core.config.storage.media_storage.backends.tenant_aware_media_storage_mixin import TenantAwareMediaStorageMixin


class TenantS3Storage(TenantAwareMediaStorageMixin, S3Storage):
    """ Store media files under a tenant-specific folder on S3-compatible backends. """
