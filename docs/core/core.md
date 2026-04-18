# Core Package

This document describes the purpose of the `core/` package and how it is used in this project.

See also:

- `docs/project.md`
- `docs/core/celery/celery.md`
- `docs/core/celery/tasks/tasks.md`
- `docs/core/config/config.md`
- `docs/core/config/logging/logging.md`
- `docs/core/config/logging/usage.md`
- `docs/core/config/storage/storage.md`
- `docs/core/config/storage/testing.md`
- `docs/core/mail/mail.md`
- `docs/core/mail/runtime.md`
- `docs/core/mail/templates.md`
- `docs/core/mail/composers.md`
- `docs/core/adminsites/adminsites.md`
- `docs/core/adminsites/owner-managed-apps.md`
- `docs/accounts/accounts.md`
- `docs/tenancy/tenancy.md`
- `docs/tenancy/runtime.md`
- `docs/tenancy/access.md`

## What `core/` Contains

The `core/` package is the Django project package. It contains the project-level configuration and entrypoints that tie the whole application together.

Current contents:

- `settings.py`
- `urls.py`
- `asgi.py`
- `wsgi.py`
- `celery.py`
- `adminsites/`
- `config/`
- `mail/`
- `testing/`
- `tests/`

Current runtime app scope wired by `core/settings.py`:

- `accounts`
- `tenancy`

## Responsibilities

The `core/` package is responsible for:

- defining global Django settings
- wiring project-level URLs
- exposing ASGI and WSGI entrypoints
- hosting shared custom admin site infrastructure
- hosting reusable project-wide configuration code
- hosting reusable project-wide logging configuration code
- hosting reusable project-wide asynchronous task runtime wiring
- hosting reusable project-wide outbound mail infrastructure
- hosting reusable testing infrastructure and project-level tests

## What Should Live Here

Code should live in `core/` when it is truly project-wide and does not belong to a single domain app.

Examples:

- environment-driven settings resolution
- Celery bootstrap shared by the whole project
- storage configuration shared by the whole project
- outbound mail infrastructure shared by the whole project
- shared admin site classes and site-level Unfold integration
- reusable test utilities
- project-level integration tests

## What Should Not Live Here

Do not place domain logic in `core/` when it belongs to a real app such as:

- `accounts`

Examples of code that should stay outside `core/`:

- model business rules
- domain query logic
- app-specific admin logic
- DTOs or factories tied to one app

For app-owned boundaries, see:

- `docs/accounts/accounts.md`
- `docs/tenancy/tenancy.md`
- `docs/tenancy/runtime.md`
- `docs/tenancy/access.md`

## Internal Structure

### `core/config/`

Contains project-level configuration modules that are too large or too specific to keep inline inside `settings.py`.

See:

- `docs/core/config/config.md`
- `docs/core/config/storage/storage.md`
- `docs/core/config/storage/testing.md`

### `core/celery.py`

Contains the project-wide Celery bootstrap used for reusable asynchronous task execution.

See:

- `docs/core/celery/celery.md`

### `core/mail/`

Contains the project-wide outbound mail service and its supporting DTO, backend, and factory layers.

See:

- `docs/core/mail/mail.md`
- `docs/core/mail/runtime.md`
- `docs/core/mail/templates.md`

### `core/adminsites/`

Contains the custom admin site infrastructure shared by the project.

See:

- `docs/core/adminsites/adminsites.md`

### `core/testing/`

Contains reusable testing infrastructure shared across multiple test modules.

Examples:

- logged test mixins
- logged base test cases

### `core/tests/`

Contains project-level tests that do not belong to a single domain app.

Current examples:

- storage adapter tests
- storage integration tests
- outbound mail service tests

## Maintenance Rule

Keep `core/` focused on project-wide concerns.

If a module starts depending heavily on one app's domain, move it into that app instead of growing `core/` further.
