# Storage Configuration

This document summarizes the supported `media` and `staticfiles` combinations, which environment variables are used in each case, and how to run the real integration tests.

## Configuration Structure

Storage configuration lives under:

- `core/config/storage/common.py`
- `core/config/storage/media_storage/`
- `core/config/storage/static_storage/`

`media` and `staticfiles` share the same storage namespace, but they keep separate contracts:

- `MediaStorageConfig`
- `StaticStorageConfig`

## Ready-To-Copy Examples

Minimal examples for the supported scenarios live in `docs/env-examples/`:

- `.env.local.local.example`
- `.env.s3.local.example`
- `.env.s3.whitenoise.example`
- `.env.s3.s3.example`
- `.env.r2.local.example`
- `.env.r2.whitenoise.example`
- `.env.r2.r2.example`

## Main Variables

### Media

- `MEDIAFILES_PROVIDER`
  - options: `local`, `s3`, `r2`
- `MEDIA_URL`
- `MEDIA_ROOT`
- `MEDIAFILES_LOCATION`

### Staticfiles

- `STATICFILES_PROVIDER`
  - options: `local`, `whitenoise`, `s3`, `r2`
- `STATIC_URL`
- `STATIC_ROOT`
- `STATICFILES_LOCATION`

### Shared Django Variables

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`
- `DB_SCHEMA`

### Shared Remote Storage Variables

These variables are used when `MEDIAFILES_PROVIDER` or `STATICFILES_PROVIDER` is set to `s3` or `r2`.

- `AWS_STORAGE_BUCKET_NAME`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_REGION_NAME`
- `AWS_S3_ENDPOINT_URL`
- `AWS_S3_CUSTOM_DOMAIN`
- `AWS_DEFAULT_ACL`
- `AWS_S3_FILE_OVERWRITE`
- `AWS_QUERYSTRING_AUTH`
- `AWS_S3_SIGNATURE_VERSION`
- `AWS_S3_ADDRESSING_STYLE`
- `CLOUDFLARE_R2_ACCOUNT_ID`

Note:

- if `AWS_S3_ENDPOINT_URL` is empty and the remote provider is `r2`, the endpoint is derived from `CLOUDFLARE_R2_ACCOUNT_ID`

### Docker-Only Variables

These variables are for `docker-compose.yml`. Django does not need them unless you explicitly choose to read them from Python.

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`
- `MINIO_ROOT_USER`
- `MINIO_ROOT_PASSWORD`
- `MINIO_API_PORT`
- `MINIO_CONSOLE_PORT`
- `MINIO_BUCKET_NAME`

## Supported Combinations

### 1. Local + Local

- `MEDIAFILES_PROVIDER=local`
- `STATICFILES_PROVIDER=local`

Use case:

- simple local development
- no bucket
- no WhiteNoise

Important variables:

- `MEDIA_URL`
- `MEDIA_ROOT`
- `STATIC_URL`
- `STATIC_ROOT`

### 2. Remote Media + Local Staticfiles

- `MEDIAFILES_PROVIDER=s3` or `r2`
- `STATICFILES_PROVIDER=local`

Use case:

- local development with remote uploads
- static files served locally

Important variables:

- all media variables
- `AWS_*`
- `MEDIAFILES_LOCATION`
- `CLOUDFLARE_R2_ACCOUNT_ID` when the provider is `r2`

### 3. Remote Media + WhiteNoise Staticfiles

- `MEDIAFILES_PROVIDER=s3` or `r2`
- `STATICFILES_PROVIDER=whitenoise`

Use case:

- simple deployment
- remote uploads
- static files served by Django and WhiteNoise

Important variables:

- `AWS_*` for media
- `STATIC_ROOT`
- `CLOUDFLARE_R2_ACCOUNT_ID` when the provider is `r2`

Note:

- this requires `whitenoise` to be installed

### 4. Remote Media + Remote Staticfiles

- `MEDIAFILES_PROVIDER=s3` or `r2`
- `STATICFILES_PROVIDER=s3` or `r2`

Use case:

- staging or production with remote buckets for both

Important variables:

- `AWS_*`
- `MEDIAFILES_LOCATION`
- `STATICFILES_LOCATION`
- `CLOUDFLARE_R2_ACCOUNT_ID` when the provider is `r2`

Recommendation:

- use different prefixes inside the bucket:
  - `media`
  - `static`

### 5. Local Media + WhiteNoise Staticfiles

- `MEDIAFILES_PROVIDER=local`
- `STATICFILES_PROVIDER=whitenoise`

Use case:

- simple deployment without a remote upload bucket

Important variables:

- `MEDIA_ROOT`
- `STATIC_ROOT`

## About `MEDIAFILES_LOCATION` and `STATICFILES_LOCATION`

These variables do not replace `MEDIA_URL` and `STATIC_URL`.

- `MEDIA_URL` and `STATIC_URL` define the public URL
- `MEDIAFILES_LOCATION` and `STATICFILES_LOCATION` define the internal prefix inside the bucket

Example:

```env
AWS_S3_CUSTOM_DOMAIN=cdn.example.com
MEDIA_URL=/media/
STATIC_URL=/static/
MEDIAFILES_LOCATION=media
STATICFILES_LOCATION=static
```

Conceptual result:

- media objects live under `media/...`
- static objects live under `static/...`
- public delivery can be served through a CDN or custom domain

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

### How They Are Organized

- `StorageIntegrationMixin` contains shared integration helpers
- `BaseStorageIntegrationSimpleTestCase` defines the shared real test cases
- `TestS3StorageIntegration` runs those cases when `MEDIAFILES_PROVIDER=s3`
- `TestR2StorageIntegration` runs those cases when `MEDIAFILES_PROVIDER=r2`

### What They Currently Cover

With `boto3`:

- list bucket contents
- upload an object
- delete an object

With `django-storages`:

- save an object
- verify existence
- build a URL
- delete an object

### How To Run Them

#### Full Storage Suite

```powershell
.\.venv\Scripts\python.exe manage.py test core.tests.storage
```

This runs:

- adapter unit tests
- integration tests, which run or skip depending on the provider and `RUN_STORAGE_INTEGRATION_TESTS`

#### R2 Integration Only

```powershell
.\.venv\Scripts\python.exe manage.py test core.tests.storage.integration.test_r2_storage_integration
```

Requirements:

- `MEDIAFILES_PROVIDER=r2`
- `RUN_STORAGE_INTEGRATION_TESTS=True`

#### S3 Integration Only

```powershell
.\.venv\Scripts\python.exe manage.py test core.tests.storage.integration.test_s3_storage_integration
```

Requirements:

- `MEDIAFILES_PROVIDER=s3`
- `RUN_STORAGE_INTEGRATION_TESTS=True`

### Proxy Note

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
