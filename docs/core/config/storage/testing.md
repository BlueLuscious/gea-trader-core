# Storage Testing

This document explains the real storage integration tests and how to run them safely.

See also:

- `docs/core/config/storage/storage.md`
- `docs/project.md`

## Optional Integration Toggle

- `RUN_STORAGE_INTEGRATION_TESTS=True`

This enables real tests against a configured S3-compatible backend.

Useful for:

- local MinIO
- S3
- R2

## Real Integration Tests

The real integration tests live in:

- `core/tests/storage/integration/base.py`
- `core/tests/storage/integration/mixins.py`
- `core/tests/storage/integration/protocols.py`
- `core/tests/storage/integration/test_s3_storage_integration.py`
- `core/tests/storage/integration/test_r2_storage_integration.py`

## How They Are Organized

- `StorageIntegrationMixin` contains shared integration helpers
- `BaseStorageIntegrationSimpleTestCase` defines the shared real test cases
- `TestS3StorageIntegration` runs those cases when `MEDIAFILES_PROVIDER=s3`
- `TestR2StorageIntegration` runs those cases when `MEDIAFILES_PROVIDER=r2`

## What They Currently Cover

With `boto3`:

- list bucket contents
- upload an object
- delete an object

With `django-storages`:

- save an object
- verify existence
- build a URL
- delete an object

## How To Run Them

### Full Storage Suite

```powershell
.\.venv\Scripts\python.exe manage.py test core.tests.storage
```

This runs:

- adapter unit tests
- integration tests, which run or skip depending on the provider and `RUN_STORAGE_INTEGRATION_TESTS`

### R2 Integration Only

```powershell
.\.venv\Scripts\python.exe manage.py test core.tests.storage.integration.test_r2_storage_integration
```

Requirements:

- `MEDIAFILES_PROVIDER=r2`
- `RUN_STORAGE_INTEGRATION_TESTS=True`

### S3 Integration Only

```powershell
.\.venv\Scripts\python.exe manage.py test core.tests.storage.integration.test_s3_storage_integration
```

Requirements:

- `MEDIAFILES_PROVIDER=s3`
- `RUN_STORAGE_INTEGRATION_TESTS=True`

## Proxy Note

If the environment has `HTTP_PROXY`, `HTTPS_PROXY`, or `ALL_PROXY` configured, `boto3` may try to route through an invalid proxy and fail even when the adapter is correct.

If that happens, clear those variables before running the suite:

```powershell
Remove-Item Env:HTTP_PROXY -ErrorAction SilentlyContinue
Remove-Item Env:HTTPS_PROXY -ErrorAction SilentlyContinue
Remove-Item Env:ALL_PROXY -ErrorAction SilentlyContinue
Remove-Item Env:http_proxy -ErrorAction SilentlyContinue
Remove-Item Env:https_proxy -ErrorAction SilentlyContinue
Remove-Item Env:all_proxy -ErrorAction SilentlyContinue
$env:NO_PROXY='*'
$env:no_proxy='*'
```
