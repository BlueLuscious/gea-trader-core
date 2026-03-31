""" Protocol definitions for storage integration tests. """

from typing import Protocol


class S3ClientProtocol(Protocol):
    """ Define the subset of boto3 S3 client methods used by integration tests. """

    def list_objects_v2(self, **kwargs: object) -> dict[str, object]:
        """ List S3 objects using boto3-compatible keyword arguments. """

    def put_object(self, **kwargs: object) -> dict[str, object]:
        """ Upload an S3 object using boto3-compatible keyword arguments. """

    def delete_object(self, **kwargs: object) -> dict[str, object]:
        """ Delete an S3 object using boto3-compatible keyword arguments. """
