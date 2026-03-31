""" Cloudflare R2 media storage adapter. """

import os
from core.config.storage.media_storage.s3 import S3MediaStorageAdapter


class R2MediaStorageAdapter(S3MediaStorageAdapter):
    """ Build media storage settings for Cloudflare R2. """

    provider = "r2"

    def build_storage_options(self) -> dict[str, object]:
        """ Build R2 media storage options from environment variables.

        Returns:
            dict[str, object]: Keyword arguments for the R2-compatible media backend.
        """
        options = super().build_storage_options()
        if not options["endpoint_url"]:
            account_id = os.environ.get("CLOUDFLARE_R2_ACCOUNT_ID", "").strip()
            if account_id:
                options["endpoint_url"] = f"https://{account_id}.r2.cloudflarestorage.com"
        return options
