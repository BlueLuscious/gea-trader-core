""" Shared mixins for storage integration tests. """

import boto3
from importlib import import_module
from botocore.client import Config as BotoConfig
from django.core.files.storage import Storage
from core.config.storage.media_storage.base_media_storage_adapter import MediaStorageConfig
from core.tests.storage.integration.protocols import S3ClientProtocol


class StorageIntegrationMixin:
    """ Provide helper methods for remote storage integration tests. """

    expected_provider: str
    storage_config: MediaStorageConfig

    def build_boto3_client(self) -> S3ClientProtocol:
        """ Build a boto3 client using the configured S3-compatible backend.

        Returns:
            S3ClientProtocol: Configured boto3 S3 client.
        """
        storage_options: dict[str, object] = self.storage_config.storages["default"]["OPTIONS"]
        client = boto3.client(
            service_name="s3",
            endpoint_url=str(storage_options.get("endpoint_url") or ""),
            aws_access_key_id=str(storage_options.get("access_key") or ""),
            aws_secret_access_key=str(storage_options.get("secret_key") or ""),
            region_name=str(storage_options.get("region_name") or ""),
            config=BotoConfig(
                signature_version=storage_options.get("signature_version") or "s3v4",
                s3={"addressing_style": storage_options.get("addressing_style") or "auto"},
            ),
        )
        return client

    def build_django_storage(self) -> Storage:
        """ Build the configured django-storages backend directly.

        Returns:
            Storage: Configured Django storage backend instance.
        """
        storage_definition = self.storage_config.storages["default"]
        backend_path = str(storage_definition["BACKEND"])
        module_path, class_name = backend_path.rsplit(".", 1)
        backend_class = getattr(import_module(module_path), class_name)
        return backend_class(**storage_definition["OPTIONS"])

    def build_object_key(self, suffix: str) -> str:
        """ Build a namespaced object key for the current provider.

        Args:
            suffix: Unique suffix for the object inside the healthchecks prefix.

        Returns:
            str: Provider-specific object key.
        """
        return f"healthchecks/{self.expected_provider}-{suffix}"

    def delete_object_if_present(self, client: S3ClientProtocol, bucket_name: str, object_key: str) -> None:
        """ Delete a remote object when it exists.

        Args:
            client: Configured boto3 S3 client.
            bucket_name: Bucket where the object may exist.
            object_key: Object key that should be removed.
        """
        objects_response = client.list_objects_v2(Bucket=bucket_name, Prefix=object_key)
        object_keys = [item["Key"] for item in objects_response.get("Contents", [])]
        if object_key in object_keys:
            client.delete_object(Bucket=bucket_name, Key=object_key)
