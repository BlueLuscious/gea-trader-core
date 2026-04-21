# Front App

This document explains the current role of `front/` and the intended future process for wiring frontend surfaces.

See also:

- `docs/project.md`
- `docs/tenancy/tenancy.md`
- `docs/tenancy/runtime.md`
- `docs/tenancy/resolution.md`

## Current Status

`front/` is now the active home for reusable UI components and public pages.

At the moment:

- it is part of the runtime URL graph wired by `core/urls.py`
- it remains decoupled from owner-admin concerns
- the current public site assumes one active tenant for the whole website
- the visual storefront implementation is still being phased in on top of that single-tenant public mode

This means the current public surface does not force tenant identity into the route.

## Future Frontend Surface Types

The future frontend can evolve into more than one kind of surface:

- tenant-aware frontend routes whose URL explicitly identifies the tenant
- global frontend routes that are not tenant-aware
- public or anonymous routes that do not require tenant membership
- authenticated tenant routes that require an active tenant and tenant-scoped permissions

These should stay explicit. One frontend surface should not silently adopt the rules of another.

## Future Tenant-Aware Frontend By Path

Path-based tenant identity remains the preferred future direction when the public site needs to support more than one tenant.

Example patterns:

- `/t/<tenant-slug>/products/`
- `/t/<tenant-slug>/quotes/`
- `/t/<tenant-slug>/checkout/`

Future process:

1. define one stable path convention for tenant-aware frontend routes
2. resolve tenant identity from the URL before page-specific business logic runs
3. keep tenant resolution separate from access policy checks
4. validate tenant membership or tenant visibility after resolution, not inside the path parser
5. keep non-tenant-aware frontend routes outside that path contract

The current public front does not use this path contract yet.
If path-based tenant resolution later becomes active, the resolution implementation should move down into `tenancy/` while the route contract stays explicit.

## Current Wiring For The Single-Tenant Public Site

The current public-site wiring follows this shape:

1. public routes stay tenant-agnostic in shape
2. the site resolves one active tenant in the view layer
3. data queries are scoped to that resolved tenant
4. links generated inside the surface stay tenant-agnostic
5. shared components remain agnostic and do not embed tenant-resolution rules by themselves

This keeps:

- single-tenant public-site assumptions in the front layer for now
- data scoping in the app layer
- rendering concerns in the frontend layer

## Current Public Storefront Surface

The current single-tenant public site now exposes:

1. one real public home page
2. one public product list page
3. one public category index page
4. one public category detail page with subcategory filtering and pagination
5. one product detail page with active-variant selection for quote cart flow
6. one sandbox page for component work

The current home page is no longer limited to the first hero block.
It now includes:

- one hero section with featured products and highlighted root categories
- one recent-products section
- one root-categories section
- one public footer with branding, contact details, social links, and a WhatsApp shortcut when configured
- one favicon wired from tenant branding with light and dark variants when available

This keeps the public site:

- incremental
- iteration-friendly
- grounded in one real storefront shell rather than isolated mock sections

## Current Non-Tenant-Aware And Public Pages

When a frontend page is not tenant-aware:

- do not force an active tenant into the route
- do not depend on tenant-scoped query filters
- do not import tenant-aware policies unless the page explicitly transitions into a tenant-aware flow

Current examples:

- `/`
- `/productos/`
- `/productos/<slug>/`
- `/categorias/`
- `/categorias/<slug>/`
- `/sandbox/`

## Current Single-Tenant Storefront Wiring

The current public storefront resolves one active tenant in the view layer and uses that tenant to provide:

- storefront branding such as display name, logos, and favicons
- public contact channels such as email, phone number, WhatsApp, and social links
- product and category query scoping for all public catalog routes
- shared navigation links that stay tenant-agnostic in route shape

This means the current storefront is still public and tenant-agnostic in its URLs, while remaining tenant-scoped in its data and branding.

## Design Rules

When wiring future frontend routes:

- prefer explicit tenant identity in the URL over implicit tenant context
- do not infer tenant context inside reusable UI components
- do not let owner-admin routing rules leak into frontend pages
- keep path-based tenant resolution and tenant access policy as separate steps
- keep the current single-tenant public mode small and explicit instead of pretending it is already multi-tenant
