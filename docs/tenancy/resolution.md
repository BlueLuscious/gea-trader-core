# Tenancy Resolution

This document explains the active-tenant resolution layer inside `tenancy/`.

See also:

- `docs/project.md`
- `docs/tenancy/tenancy.md`
- `docs/tenancy/runtime.md`
- `docs/tenancy/access.md`
- `docs/core/adminsites/adminsites.md`

## Goal

The resolution layer exists to answer one question consistently:

- which tenant is active for this request?

This decision is infrastructure-level and should stay separate from:

- tenant persistence
- tenant access policies
- explicit tenant switching

## Current Structure

Current runtime structure:

```text
tenancy/
  resolution/
    active_tenant_resolver.py
    admin_active_tenant_resolver.py
    composite_tenant_resolver.py
    strategies/
      tenant_resolution_strategy.py
      session_tenant_resolution_strategy.py
      membership_tenant_resolution_strategy.py
      path_tenant_resolution_strategy.py
```

## Responsibilities

The resolution layer is responsible for:

- defining the contract for one tenant-resolution strategy
- composing multiple strategies in one resolver
- keeping the current admin resolution order explicit
- making future resolution styles possible without rewriting middleware

It is not responsible for:

- deciding whether a user may manage a tenant
- storing the active tenant in session
- switching tenants explicitly from one UI action

Those concerns belong to:

- `tenancy/access/`
- `tenancy/session/`
- `tenancy/switching/`

## Current Resolver Flow

Today the middleware uses:

- `ActiveTenantResolver`

That class currently delegates to:

- `AdminActiveTenantResolver`

The admin resolver currently composes:

1. `SessionTenantResolutionStrategy`
2. `MembershipTenantResolutionStrategy`

This preserves the current runtime behavior:

1. tenant stored in session
2. primary active membership
3. first active membership

## Current Components

### `TenantResolutionStrategy`

This is the base contract for one strategy.

It defines:

- `resolve(request) -> TenantModel | None`

Each strategy should:

- inspect one source of truth
- either return one tenant
- or return `None`

It should not:

- make authorization decisions
- mutate unrelated request state
- know about every possible resolution mode

### `CompositeTenantResolver`

This resolver takes a list of strategies and runs them in order.

The first strategy that returns a tenant wins.

This keeps the flow:

- explicit
- ordered
- easy to test

### `AdminActiveTenantResolver`

This is the current composed resolver for admin flows.

It adds one admin-specific behavior before strategy execution:

- anonymous users clear the active-tenant session marker and resolve to `None`

After that, it delegates to the configured strategies.

## Current Strategies

### `SessionTenantResolutionStrategy`

This strategy tries to resolve the active tenant from session state.

Current behavior:

- read tenant id from session
- verify the authenticated user still has one active membership for that tenant
- return the tenant when valid
- clear the session marker when it is stale

Use case:

- owner switches tenant from the dropdown
- the next request keeps that selection

### `MembershipTenantResolutionStrategy`

This is the fallback strategy for the current runtime.

Current behavior:

- inspect active memberships for the authenticated user
- order them for deterministic fallback
- prefer primary membership first
- otherwise use the first active membership
- persist the fallback tenant into session

Use case:

- user signs in with no active tenant stored in session
- system chooses a stable default tenant automatically

### `PathTenantResolutionStrategy`

This strategy exists today as a deliberate future extension point.

Current behavior:

- always returns `None`

It is intentionally present because the future frontend may need tenant resolution from the URL path.

Example future URL patterns:

- `/t/<tenant-slug>/products/`
- `/t/<tenant-slug>/quotes/`
- `/t/<tenant-slug>/checkout/`

Possible future behavior:

- extract `tenant_slug` from path params or resolver kwargs
- load `TenantModel` by slug
- optionally validate user access depending on the surface

This strategy is not wired into the current middleware yet.

## Future Strategy Options

The current design allows additional strategies without rewriting the whole resolver.

### Future `PathTenantResolutionStrategy`

Best fit:

- tenant-aware frontend routes
- APIs whose URL already contains tenant identity

Pros:

- explicit tenant context in the URL
- easy to reason about for frontend apps
- works well for future non-Django frontends consuming APIs

Tradeoffs:

- requires stable tenant path conventions
- requires routing decisions across frontend and backend

### Future `HostTenantResolutionStrategy`

A host-based strategy is also a reasonable future option.

Example patterns:

- `acme.example.com`
- `north-center.example.com`

Possible future behavior:

- inspect `request.get_host()`
- map subdomain or host to one tenant
- return the matching tenant

Best fit:

- SaaS-style tenant isolation by subdomain
- branded tenant-specific frontend surfaces

Tradeoffs:

- more infrastructure complexity
- DNS and environment setup matter more
- less convenient for quick admin context switching

## Future Path-Based Frontend Wiring Process

When the first real tenant-aware frontend surface appears, the recommended process is:

1. choose one stable route contract for tenant-aware pages
2. activate `PathTenantResolutionStrategy` before adding page-specific tenant logic
3. resolve the tenant from the route
4. apply access policy checks after tenant resolution
5. scope queries and service calls to the resolved tenant
6. keep owner-admin session switching independent from frontend path-based routing

This future flow should not replace the current admin resolver. It should add one new composed resolver for the frontend surface when that surface becomes real.

## Future Non-Tenant-Aware Frontend Process

Not every frontend page should become tenant-aware.

For future frontend surfaces that are global or anonymous:

- do not wire path-based tenant resolution
- do not require an active tenant in the route
- do not mix frontend-global pages with tenant-bound resolution rules

This keeps tenant-aware routing explicit instead of gradually leaking into unrelated pages.

## Recommended Resolution Modes By Surface

### Owner Admin

Recommended mode:

- session first
- membership fallback

Reason:

- one owner may switch between multiple tenants quickly
- URL shape does not need to change

### Future Frontend

Recommended mode:

- path-based resolution first

Reason:

- tenant context should be explicit in the route
- easier to support future API consumers and external frontends

### Future SaaS Host Routing

Recommended mode:

- host-based resolution when subdomain tenancy becomes a product requirement

Reason:

- best for strong tenant identity in the URL
- not necessary for the current runtime

## Design Rules

When adding a new resolution strategy:

- keep it small
- keep it focused on one source of truth
- return `None` when it does not apply
- do not mix access policy rules into the strategy
- do not make the middleware branch on many special cases

When adding a new composed resolver:

- name it after the surface it serves
- keep the strategy order explicit
- document its expected precedence

## Current Logging Direction

The resolution layer now logs only the runtime boundaries that help explain how one request obtained its active tenant.

Current examples:

- which strategy resolved the tenant inside the composite resolver
- when an anonymous-like request clears the active-tenant session marker
- when a stale session-selected tenant is discarded
- when membership fallback chooses and persists one tenant

Current rule:

- keep logs at resolver and strategy boundaries
- do not add noisy logs to every membership or queryset helper that participates indirectly in resolution

## Current Status

Implemented now:

- base strategy contract
- session strategy
- membership fallback strategy
- composite resolver
- admin resolver

Designed but not activated:

- path-based tenant resolution
- host-based tenant resolution

This keeps the current admin flow stable while giving the project a clear path for future tenant-aware frontend work.
