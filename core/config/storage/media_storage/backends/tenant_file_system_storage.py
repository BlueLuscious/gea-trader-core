""" Local filesystem media backend with tenant-aware path prefixing. """

from django.core.files.storage import FileSystemStorage
from core.config.storage.media_storage.backends.tenant_aware_media_storage_mixin import TenantAwareMediaStorageMixin


class TenantFileSystemStorage(TenantAwareMediaStorageMixin, FileSystemStorage):
    """ Store media files under a tenant-specific folder on the local filesystem. """
