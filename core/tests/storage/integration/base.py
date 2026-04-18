""" Shared base test cases for storage integration tests. """

import os
from unittest import SkipTest
from django.conf import settings
from django.core.files.base import ContentFile
from core.config.storage import MediaStorageAdapterResolver
from core.config.storage.media_storage.adapters import MediaStorageConfig
from core.testing.base import LoggedSimpleTestCase
from core.tests.storage.integration.mixins import StorageIntegrationMixin


def is_storage_integration_enabled() -> bool:
    """ Return whether storage integration tests should run.

    Returns:
        bool: True when storage integration tests are explicitly enabled.
    """
    return os.environ.get("RUN_STORAGE_INTEGRATION_TESTS", "False").lower() in ("1", "true", "yes", "on")


class BaseStorageIntegrationSimpleTestCase(StorageIntegrationMixin, LoggedSimpleTestCase):
    """ Define shared remote storage integration tests for one expected provider. """

    expected_provider: str = ""
    storage_config: MediaStorageConfig

    @classmethod
    def setUpClass(cls) -> None:
        """ Skip the suite when integration env vars do not match the expected provider. """
        super().setUpClass()

        if not is_storage_integration_enabled():
            raise SkipTest("Storage integration tests are disabled.")

        cls.storage_config = MediaStorageAdapterResolver.build_config(settings.BASE_DIR)
        if cls.storage_config.provider != cls.expected_provider:
            raise SkipTest(f"Storage integration tests require MEDIAFILES_PROVIDER={cls.expected_provider}.")

    def test_storage_integration__boto3_can_list_bucket(self) -> None:
        """ Verify boto3 can list the configured bucket without failing authentication. """
        client = self.build_boto3_client()
        bucket_name = str(self.storage_config.storages["default"]["OPTIONS"]["bucket_name"])
        response = client.list_objects_v2(Bucket=bucket_name, Prefix="healthchecks/")

        self.assertIn("ResponseMetadata", response)

    def test_storage_integration__boto3_can_put_object(self) -> None:
        """ Verify boto3 can upload an object into the configured bucket. """
        client = self.build_boto3_client()
        bucket_name = str(self.storage_config.storages["default"]["OPTIONS"]["bucket_name"])
        object_key = self.build_object_key("boto3-put-test.txt")

        self.delete_object_if_present(client, bucket_name, object_key)
        client.put_object(Bucket=bucket_name, Key=object_key, Body=f"ok desde boto3 {self.expected_provider}".encode())

        objects_response = client.list_objects_v2(Bucket=bucket_name, Prefix=object_key)
        object_keys = [item["Key"] for item in objects_response.get("Contents", [])]
        self.assertIn(object_key, object_keys)

    def test_storage_integration__boto3_can_delete_object(self) -> None:
        """ Verify boto3 can delete an uploaded object from the configured bucket. """
        client = self.build_boto3_client()
        bucket_name = str(self.storage_config.storages["default"]["OPTIONS"]["bucket_name"])
        object_key = self.build_object_key("boto3-delete-test.txt")

        client.put_object(Bucket=bucket_name, Key=object_key, Body=f"delete me {self.expected_provider}".encode())
        client.delete_object(Bucket=bucket_name, Key=object_key)

        objects_response = client.list_objects_v2(Bucket=bucket_name, Prefix=object_key)
        object_keys = [item["Key"] for item in objects_response.get("Contents", [])]
        self.assertNotIn(object_key, object_keys)

    def test_storage_integration__django_storage_can_save_object(self) -> None:
        """ Verify django-storages can save an object in the configured bucket. """
        storage = self.build_django_storage()
        object_key = self.build_object_key("django-save-test.txt")

        storage.delete(object_key)
        saved_name = storage.save(object_key, ContentFile(f"ok desde django {self.expected_provider}".encode()))

        self.assertEqual(saved_name, object_key)
        self.assertTrue(storage.exists(saved_name))

    def test_storage_integration__django_storage_can_check_object_existence(self) -> None:
        """ Verify django-storages can report existence for a saved object. """
        storage = self.build_django_storage()
        object_key = self.build_object_key("django-exists-test.txt")

        storage.delete(object_key)
        saved_name = storage.save(object_key, ContentFile(f"ok desde django {self.expected_provider}".encode()))
        self.assertTrue(storage.exists(saved_name))

    def test_storage_integration__django_storage_can_build_object_url(self) -> None:
        """ Verify django-storages can build a public URL for a saved object. """
        storage = self.build_django_storage()
        object_key = self.build_object_key("django-url-test.txt")

        storage.delete(object_key)
        saved_name = storage.save(object_key, ContentFile(f"ok desde django {self.expected_provider}".encode()))
        resolved_url = storage.url(saved_name)
        self.assertTrue(bool(resolved_url))

    def test_storage_integration__django_storage_can_delete_object(self) -> None:
        """ Verify django-storages can delete an object from the configured bucket. """
        storage = self.build_django_storage()
        object_key = self.build_object_key("django-delete-test.txt")

        storage.delete(object_key)
        saved_name = storage.save(object_key, ContentFile(f"ok desde django {self.expected_provider}".encode()))
        storage.delete(saved_name)
        self.assertFalse(storage.exists(saved_name))
