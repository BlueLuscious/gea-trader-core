# Front App

This document explains the current role of `front/` and the intended future process for wiring frontend surfaces.

See also:

- `docs/project.md`
- `docs/tenancy/tenancy.md`
- `docs/tenancy/runtime.md`
- `docs/tenancy/resolution.md`

## Current Status

`front/` exists as the intended home for reusable UI components, pages, and future frontend routes.

At the moment:

- it is not the primary documented runtime surface of the project
- it is not part of the current runtime app scope wired by `core/settings.py`
- it should remain decoupled from owner-admin concerns
- it should only become tenant-aware when a real tenant-aware frontend flow exists

This means the project should not pre-emptively force tenant awareness into every frontend page.

## Future Frontend Surface Types

The future frontend can evolve into more than one kind of surface:

- tenant-aware frontend routes whose URL explicitly identifies the tenant
- global frontend routes that are not tenant-aware
- public or anonymous routes that do not require tenant membership
- authenticated tenant routes that require an active tenant and tenant-scoped permissions

These should stay explicit. One frontend surface should not silently adopt the rules of another.

## Future Tenant-Aware Frontend By Path

When the first tenant-aware frontend flow appears, the preferred direction is path-based tenant identity.

Example patterns:

- `/t/<tenant-slug>/products/`
- `/t/<tenant-slug>/quotes/`
- `/t/<tenant-slug>/checkout/`

Recommended process:

1. define one stable path convention for tenant-aware frontend routes
2. resolve tenant identity from the URL before page-specific business logic runs
3. keep tenant resolution separate from access policy checks
4. validate tenant membership or tenant visibility after resolution, not inside the path parser
5. keep non-tenant-aware frontend routes outside that path contract

The preferred backend support for this future flow is already described in `docs/tenancy/resolution.md` through the planned `PathTenantResolutionStrategy`.

## Recommended Wiring For Future Tenant-Aware Frontend Pages

When a new tenant-aware frontend page is introduced, the expected wiring should be:

1. route includes a stable tenant identifier, preferably the tenant slug
2. tenant is resolved from the route by the dedicated resolution strategy
3. page access checks are applied after tenant resolution
4. data queries are scoped to the resolved tenant
5. links generated inside that surface preserve the tenant path contract
6. shared components remain agnostic and should not embed tenant-resolution rules by themselves

This keeps:

- resolution in the resolution layer
- authorization in the access layer
- data scoping in the app layer
- rendering concerns in the frontend layer

## Recommended Wiring For Future Non-Tenant-Aware Frontend Pages

When a frontend page is not tenant-aware:

- do not force an active tenant into the route
- do not depend on tenant-scoped query filters
- do not import tenant-aware policies unless the page explicitly transitions into a tenant-aware flow

Examples:

- landing pages
- marketing pages
- generic sign-in flows
- documentation or support pages

## Design Rules

When wiring future frontend routes:

- prefer explicit tenant identity in the URL over implicit tenant context
- do not infer tenant context inside reusable UI components
- do not let owner-admin routing rules leak into frontend pages
- keep path-based tenant resolution and tenant access policy as separate steps
- only extract reusable frontend tenant helpers after at least one real tenant-aware surface exists
