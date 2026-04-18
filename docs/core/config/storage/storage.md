# Storage Configuration

This document summarizes the supported `media` and `staticfiles` combinations and the environment variables used to wire them.

See also:

- `docs/project.md`
- `docs/core/config/config.md`
- `docs/core/config/storage/testing.md`

## Configuration Structure

Storage configuration lives under:

- `core/config/storage/common.py`
- `core/config/storage/media_storage/`
- `core/config/storage/static_storage/`

Both storage domains expose a resolver entrypoint:

- `MediaStorageAdapterResolver.build_config(...)`
- `StaticStorageAdapterResolver.build_config(...)`

These resolver boundaries are also the preferred place for operational storage logging.

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

## Current Storage Direction

The current storage design intentionally supports multiple deployment shapes without forcing one provider choice across every environment.

Current rules:

- `media` may be local or remote
- `staticfiles` may be local, WhiteNoise, or remote
- media is tenant-aware when an active tenant exists at save time
- static files remain global unless the project introduces a real tenant-specific static surface later

This means storage should be wired per surface and per environment, not by one hardcoded deployment assumption.

## Current Logging Direction

The storage layer should log at configuration and provider-resolution boundaries.

Current direction:

- log which media provider was resolved
- log which staticfiles provider was resolved
- log the selected backend class and any extra apps or middleware added by the configuration
- avoid logging every low-level helper or every derived storage option individually

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
- `MAILHOG_SMTP_PORT`
- `MAILHOG_UI_PORT`

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

Current tenancy direction:

- media is tenant-aware at runtime and stores uploaded objects under `tenants/<tenant-slug>/...` when one active tenant exists
- static files remain global unless real per-tenant branding assets are introduced

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

With tenant-aware media enabled, the final stored object key becomes:

- `media/tenants/<tenant-slug>/...` for remote backends
- `MEDIA_ROOT/tenants/<tenant-slug>/...` for local media

The tenant prefix is generated through the storage backend `generate_filename()`
hook. When saving to storage directly instead of going through a Django
`FileField` or `ImageField`, generate the final object name first and then pass
that name into `save()`.

If no active tenant exists during the save operation, media keeps the original relative path unchanged.

## Future Storage Adapter Wiring Process

When a new environment or deployment target needs storage wiring, follow this process:

1. decide whether `media` and `staticfiles` should be local, WhiteNoise-backed, or remote
2. choose the provider per surface instead of assuming both must use the same backend
3. configure the provider-specific environment variables
4. keep media tenant-aware through the existing filename generation path instead of adding tenant prefixes in views or forms
5. keep static files global unless the product introduces a real tenant-specific static requirement
6. validate the selected combination with `manage.py check`
7. run unit tests and real integration tests when the target uses an S3-compatible backend

## Future Process For Adding One New Storage Adapter

If the project eventually adds a new storage provider beyond `local`, `s3`, `r2`, or `whitenoise`, the expected process should be:

1. create the adapter config and backend classes under `core/config/storage/`
2. wire the provider into the corresponding resolver entrypoint
3. keep the provider-specific settings isolated from app-level code
4. add unit coverage for the resolver and backend behavior
5. add opt-in integration coverage only when real provider access is available
6. update this document, the storage testing document, and the environment examples

This keeps provider changes inside the storage layer instead of leaking them into domain apps.
