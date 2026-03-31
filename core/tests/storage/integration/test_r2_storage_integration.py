""" Integration tests for the Cloudflare R2 storage adapter. """

from core.tests.storage.integration import base as integration_base


class TestR2StorageIntegration(integration_base.BaseStorageIntegrationSimpleTestCase):
    """ Cover boto3 and django-storages integration against the R2 adapter. """

    expected_provider = "r2"
