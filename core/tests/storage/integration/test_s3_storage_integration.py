""" Integration tests for the S3 storage adapter. """

from core.tests.storage.integration import base as integration_base


class TestS3StorageIntegration(integration_base.BaseStorageIntegrationSimpleTestCase):
    """ Cover boto3 and django-storages integration against the S3 adapter. """

    expected_provider = "s3"
