# Project Documentation Map

This directory contains the main architectural and operational documentation for the project.

Use this file first to understand where each topic is documented and which document owns each concern.

## Current Documented Scope

The runtime code currently documented here is centered on:

- `masterdata/`
- `catalog/`
- `cart/`
- `quotation/`
- `accounts/`
- `tenancy/`
- `core/`
- `front/` as a future-facing integration surface

Current status of the other app folders:

- `front/` exists as the intended UI surface for future reusable components and tenant-aware routes, but it is not part of the current runtime app scope wired by `core/settings.py`
- `catalog/` and `quotation/` already define documented domain and owner-admin flows in this branch
- `masterdata/` now defines documented tenant-owned reference-data and owner-admin flows in this branch
- `cart/` is part of the runtime app scope wired by `core/settings.py`, but it still needs fuller owner documentation once its user-facing role stabilizes

## Project Entry Docs

- Repository setup and development workflow: `README.md`
- Capability status by implementation stage: `docs/capability-status.md`

## Core Docs

- Project package overview: `docs/core/core.md`
- Project-wide Celery runtime: `docs/core/celery/celery.md`
- Celery task conventions: `docs/core/celery/tasks/tasks.md`
- Project admin infrastructure: `docs/core/adminsites/adminsites.md`
- Future owner-managed app wiring: `docs/core/adminsites/owner-managed-apps.md`
- Project configuration overview: `docs/core/config/config.md`
- Project logging configuration: `docs/core/config/logging/logging.md`
- Logging usage rules: `docs/core/config/logging/usage.md`
- Project mail infrastructure: `docs/core/mail/mail.md`
- Mail runtime behavior: `docs/core/mail/runtime.md`
- Mail template structure: `docs/core/mail/templates.md`
- Mail composer guidance: `docs/core/mail/composers.md`
- Storage configuration details: `docs/core/config/storage/storage.md`
- Storage testing guidance: `docs/core/config/storage/testing.md`

## App Docs

- Accounts app: `docs/accounts/accounts.md`
- Catalog app: `docs/catalog/catalog.md`
- Front app and future tenant-aware UI direction: `docs/front/front.md`
- Masterdata app: `docs/masterdata/masterdata.md`
- Quotation app: `docs/quotation/quotation.md`
- Tenancy app: `docs/tenancy/tenancy.md`
- Tenancy runtime behavior: `docs/tenancy/runtime.md`
- Tenancy access policies: `docs/tenancy/access.md`
- Tenancy resolution layer: `docs/tenancy/resolution.md`

## Ownership Rule

To avoid repeating the same explanation in multiple places:

- `docs/core/core.md` owns the explanation of what belongs in `core/`
- `docs/core/celery/celery.md` owns the project-wide Celery runtime and async bootstrap
- `docs/core/celery/tasks/tasks.md` owns shared task placement and payload conventions for Celery-based async work
- `docs/core/adminsites/adminsites.md` owns admin site infrastructure details
- `docs/core/config/config.md` owns the configuration-layer boundary
- `docs/core/config/logging/logging.md` owns the shared logging configuration layer
- `docs/core/config/logging/usage.md` owns the shared logging usage rules for runtime code
- `docs/core/mail/mail.md` owns the project-wide outbound mail boundary and package structure
- `docs/core/mail/runtime.md` owns the current mail runtime behavior, async delivery direction, settings, and test guidance
- `docs/core/mail/templates.md` owns the shared mail template structure and tenant-aware template context rules
- `docs/core/mail/composers.md` owns composer usage and design guidance for the project mail stack
- `docs/core/config/storage/storage.md` owns storage provider and env-var details
- `docs/core/config/storage/testing.md` owns storage integration-test structure and execution guidance
- `docs/accounts/accounts.md` owns the `accounts/` domain structure
- `docs/catalog/catalog.md` owns the `catalog/` domain structure
- `docs/front/front.md` owns the frontend structure and future tenant-aware UI direction
- `docs/masterdata/masterdata.md` owns the `masterdata/` domain structure
- `docs/quotation/quotation.md` owns the `quotation/` domain structure
- `docs/tenancy/tenancy.md` owns the `tenancy/` domain structure and persistence-oriented app boundary
- `docs/tenancy/runtime.md` owns request-time tenant runtime behavior and switching
- `docs/tenancy/access.md` owns tenant access-policy guidance
- `docs/tenancy/resolution.md` owns the active-tenant resolution design and strategy layer

When one topic depends on another, the app or subsystem doc should link to the owning document instead of duplicating the full explanation.
