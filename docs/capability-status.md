# Capability Status Map

This document classifies the main project capabilities by implementation status.

Use it as a quick answer to questions such as:

- what already runs in production-style runtime today
- what is already implemented but not connected yet
- what is only designed as a future direction

See also:

- `docs/project.md`

## How To Read This Document

Each capability falls into one of these states:

- `Implemented now`: active in the current runtime
- `Implemented as extension point`: code or structure already exists, but it is not the active runtime path yet
- `Designed for future`: documented direction that still requires real implementation work

This document is an index, not the detailed owner of each topic.
Follow the linked docs to inspect the full rules for one capability.

## Implemented Now

### Accounts And Authentication

- custom `UserModel`
- owner and master admin registrations for users and groups
- tenant-scoped owner account management rules

Check:

- `docs/accounts/accounts.md`
- `docs/core/adminsites/adminsites.md`

### Tenancy Base

- `TenantModel`
- `TenantMembershipModel`
- `TenantGroupModel`
- `TenantBrandingModel`
- active tenant stored on `request.tenant`

Check:

- `docs/tenancy/tenancy.md`
- `docs/tenancy/runtime.md`

### Active Tenant Resolution For Admin

- middleware-driven active tenant resolution
- session-first admin flow
- membership fallback when no active tenant is stored
- explicit tenant switching through the owner admin

Check:

- `docs/tenancy/runtime.md`
- `docs/tenancy/resolution.md`

### Owner Admin Base Structure

- custom owner admin site
- tenant-aware header metadata and branding
- tenant switcher dropdown
- direct business settings flow for the active tenant
- portable redirect behavior when switching tenants from admin change views

Check:

- `docs/core/adminsites/adminsites.md`
- `docs/tenancy/runtime.md`

### Tenant-Aware Media Storage

- tenant-aware media object naming based on the active tenant
- local, S3, and R2 support for media
- local, WhiteNoise, S3, and R2 support for static files

Check:

- `docs/core/config/storage/storage.md`
- `docs/core/config/storage/testing.md`

### Core Mail Service

- project-wide outbound mail service under `core/mail/`
- synchronous delivery through Django's email stack
- asynchronous delivery through the shared Celery runtime for raw and templated mail
- DTO, backend, factory, serializer, and task layers wired for both sync and async delivery
- reusable template-based mail rendering with a shared base layout and mandatory system footer

Check:

- `docs/core/mail/mail.md`
- `docs/core/mail/runtime.md`
- `docs/core/mail/templates.md`

### Owner Favicon Theme Support

- light and dark favicon variants resolved from tenant branding
- small owner-admin script that finalizes `prefers-color-scheme` behavior in the browser

Check:

- `docs/core/adminsites/adminsites.md`
- `docs/tenancy/tenancy.md`

## Implemented As Extension Point

### Project-Wide Async Task Runtime

- Redis-backed Celery wiring already exists in `core/`
- the stack is prepared for any future asynchronous task, not only mail
- outbound mail is already running on top of the shared runtime
- future app-owned tasks can build on the same bootstrap and task conventions

Check:

- `docs/core/celery/celery.md`
- `docs/core/mail/runtime.md`

### Path-Based Tenant Resolution

- `PathTenantResolutionStrategy` already exists as a dedicated strategy hook
- it is not part of the active runtime resolver yet

Check:

- `docs/tenancy/resolution.md`
- `docs/front/front.md`

### Front App As Future UI Surface

- `front/` already exists as the intended home for reusable components and future frontend routes
- it is not part of the current runtime app scope wired by `core/settings.py`
- the project already defines how tenant-aware frontend routing should be wired once the first real surface appears

Check:

- `docs/front/front.md`
- `docs/tenancy/resolution.md`

### Future Owner-Managed App Pattern

- the project already defines the wiring contract for future owner-managed apps
- `accounts` and `tenancy` stay owner-only
- future tenant-member apps should use tenant membership plus Django permissions

Check:

- `docs/core/adminsites/owner-managed-apps.md`
- `docs/tenancy/access.md`
- `docs/accounts/accounts.md`

## Designed For Future

### Host-Based Tenancy

- host or subdomain-based tenant identity is a documented future option
- no runtime resolver is wired for it today

Check:

- `docs/tenancy/resolution.md`

### Path-Based Tenant-Aware Frontend Surface

- the route contract and wiring direction are documented
- no real frontend tenant-aware flow is active yet

Check:

- `docs/front/front.md`
- `docs/tenancy/resolution.md`

### New Domain Apps

- `catalog/`
- `cart/`
- `masterdata/`
- `quotation/`

These app folders exist in the repository, but they are not yet the primary documented runtime scope of this branch.

Check:

- `docs/project.md`

### New Storage Adapter Onboarding

- the process for adding one new storage provider is documented
- no additional provider beyond the current supported set is being added right now

Check:

- `docs/core/config/storage/storage.md`
- `docs/core/config/storage/testing.md`

## Process Families To Reuse Later

These are the main future process types that the project should reuse instead of inventing ad hoc wiring each time:

1. owner-only app wiring
2. operator-capable owner-managed app wiring
3. non-tenant-aware app wiring
4. tenant-aware frontend wiring by path
5. non-tenant-aware frontend wiring
6. admin session-based tenant switching
7. storage wiring by environment
8. tenant-aware media storage wiring
9. global staticfiles wiring
10. new storage adapter onboarding
11. host-based tenancy onboarding
12. future domain-app documentation onboarding

## Rule Of Thumb

When a capability changes status:

- update the owner document first
- update this index second
- keep local backlog tracking separate from stable architectural truth
