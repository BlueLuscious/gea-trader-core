# Core Configuration

This document explains the purpose of `core/config/` and how configuration modules should be organized there.

See also:

- `docs/project.md`
- `docs/core/core.md`
- `docs/core/config/logging/logging.md`
- `docs/core/config/logging/usage.md`
- `docs/core/config/storage/storage.md`
- `docs/core/config/storage/testing.md`

## Goal

`core/config/` exists to keep `core/settings.py` readable while still allowing structured, testable, environment-driven configuration code.

Use this package for configuration that is:

- project-wide
- environment-dependent
- reused by multiple settings values
- easier to maintain when isolated from the main settings file

## Current Structure

Current contents:

- `logging/`
- `storage/`

The `logging/` package contains configuration logic for:

- project-wide logger settings
- environment-driven log levels
- shared Django and Celery logging defaults

The `storage/` package contains configuration logic for:

- media storage
- staticfiles storage
- shared storage helpers

See:

- `docs/core/config/storage/storage.md`
- `docs/core/config/storage/testing.md`

This document owns the boundary of the configuration layer.
Detailed provider behavior, environment variables, and storage combinations belong in the storage-specific document instead of being repeated here.

## What Belongs In `core/config/`

Good candidates:

- configuration builders
- environment parsing helpers
- provider resolution
- settings-related adapter selection

Examples:

- selecting a storage provider from env vars
- building `STORAGES`
- deciding extra installed apps or middleware based on configuration

## What Does Not Belong In `core/config/`

Avoid placing these here:

- domain business logic
- model behavior
- view logic
- app-specific concerns that belong in a domain app

Also avoid turning `core/config/` into a miscellaneous utilities package.

## Design Guidelines

Prefer:

- small focused modules
- explicit contracts
- environment-driven configuration
- shared helpers only when the logic is truly shared

Avoid:

- giant builders that mix unrelated concerns
- hidden side effects
- configuration code that silently mutates global state

## Relationship With `settings.py`

`settings.py` should consume configuration from `core/config/`, not reimplement it inline.

The intended pattern is:

- `settings.py` imports a builder or public API
- `core/config/` resolves the environment and returns structured values

This keeps settings readable and makes the configuration layer easier to test.

## Maintenance Rule

If a configuration area becomes large enough to deserve its own boundary, create a dedicated subpackage inside `core/config/` rather than growing a single module indefinitely.
