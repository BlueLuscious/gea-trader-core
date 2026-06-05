# Tenancy Runtime

This document explains the current request-time tenant runtime behavior inside `tenancy/`.

See also:

- `docs/project.md`
- `docs/tenancy/tenancy.md`
- `docs/tenancy/access.md`
- `docs/tenancy/resolution.md`
- `docs/core/adminsites/adminsites.md`
- `docs/core/config/storage/storage.md`

## Goal

The tenancy runtime exists to answer one practical question consistently:

- which tenant is active for this request and how does that tenant change over time?

This runtime layer covers:

- request-time active tenant attachment
- session-backed tenant persistence
- explicit active-tenant switching
- owner-admin runtime behavior that depends on the current tenant

## Active Tenant Resolution

The base structure resolves an active tenant during the request cycle.

Current behavior:

- resolution happens through `ActiveTenantMiddleware`
- resolution currently runs only for the owner-admin URL surface
- non-tenant-aware paths attach `request.tenant = None` without running the active-tenant resolver
- middleware lives in `tenancy/middleware/`
- resolution rules live in `tenancy/resolution/`
- session persistence lives in `tenancy/session/`
- runtime request context lives in `tenancy/runtime/`
- the active tenant is stored in session
- if the session does not define one, the request falls back to the user's primary active membership
- if no primary membership exists, the first active membership is used
- the active tenant is also exposed through a runtime context helper for request-bound infrastructure such as media storage

Current request contract:

- `request.tenant` contains the resolved tenant or `None`

This keeps tenant-aware admin behavior explicit while leaving global frontend requests outside membership-backed resolution.

Request-aware storage behavior that consumes the runtime active tenant is documented in:

- `docs/core/config/storage/storage.md`

The detailed structure, strategy contract, and future path or host resolution options are documented in:

- `docs/tenancy/resolution.md`

## Explicit Tenant Switching

The base structure supports explicit tenant switching.

Current behavior:

- the app exposes `switch-active-tenant` through `tenancy/urls.py`
- it stores the selected tenant in session
- it validates that the authenticated user still has one active membership for the requested tenant
- it redirects back to a safe `next` URL when provided

Current intent:

- session state controls the current tenant context
- the primary membership remains the fallback default
- switching the active tenant does not rewrite `is_primary`

Current logging direction:

- log successful active-tenant switches with the actor and tenant id
- log rejected switch attempts when the requested tenant is not accessible
- log whether the switch view returned to one safe `next` URL or fell back to the owner admin index

## Owner-Admin Runtime Use Cases

Current runtime use cases include:

- choosing the active tenant during owner-admin work
- displaying tenant-aware owner admin metadata such as title and header
- switching tenant context explicitly from the owner admin dropdown
- keeping the native tenant settings screen bound to the active tenant

These behaviors are tenant-runtime concerns even when they are rendered inside the shared owner admin site.

## Current Logging Direction

The tenancy runtime should log at request-time resolution, switching, and owner-admin runtime boundaries.

Current direction:

- log which strategy resolved the tenant
- log stale or cleared tenant session state
- log successful and rejected active-tenant switches
- log owner-admin redirect or fallback edges that depend on the active tenant
- avoid logging every low-level membership or queryset helper indirectly involved in resolution

## Future Direction

The current implementation is intentionally centered on session-backed resolution because it fits the owner admin flow.

Future frontend work may require path-based or host-based tenant resolution without changing the current admin URL shape.

The detailed resolution roadmap, strategy breakdown, and future examples are documented in:

- `docs/tenancy/resolution.md`

## What Should Live Here

Good candidates:

- request-time tenancy middleware behavior
- session-backed active-tenant state
- explicit tenant switching behavior
- runtime tenant context rules consumed by admin and shared infrastructure

## What Should Not Live Here

Avoid placing these here:

- detailed strategy internals that already belong to the resolution layer
- generic tenant access policy definitions
- tenant persistence rules

Those concerns belong in:

- `docs/tenancy/resolution.md`
- `docs/tenancy/access.md`
- `docs/tenancy/tenancy.md`
