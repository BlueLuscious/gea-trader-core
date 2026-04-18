# Tenancy App

This document explains the purpose and structure of the `tenancy/` app.

See also:

- `docs/project.md`
- `docs/tenancy/runtime.md`
- `docs/tenancy/access.md`
- `docs/tenancy/resolution.md`
- `docs/core/core.md`
- `docs/core/adminsites/adminsites.md`
- `docs/core/config/storage/storage.md`
- `docs/accounts/accounts.md`

## Goal

`tenancy/` provides the root multitenancy domain used to scope business data across the project.

It currently defines:

- the base tenant entity
- tenant branding assets and display metadata
- tenant-to-user memberships
- tenant-to-group bindings
- role choices for tenant memberships
- typed query infrastructure for tenant data
- owner-admin business settings helpers
- master admin registrations for technical administration

The request-time runtime flow, switching behavior, and access policies are now documented separately so the app structure doc can stay focused on the domain boundary itself.

## Current Structure

Current contents:

- `apps.py`
- `constants.py`
- `urls.py`
- `choices/`
- `models/`
- `access/`
- `resolution/`
- `switching/`
- `session/`
- `runtime/`
- `middleware/`
- `views/`
- `admin/`
- `migrations/`
- `tests/`

The app still groups two families of concern inside one Django app:

- tenant persistence and membership rules
- active-tenant runtime infrastructure

Those runtime pieces stay inside `tenancy/` because they are tightly coupled to:

- `TenantModel`
- `TenantMembershipModel`
- tenant-scoped request resolution

## Responsibilities

The `tenancy/` app is responsible for:

- defining the root tenant entity
- defining how users belong to tenants
- exposing reusable tenant query helpers
- exposing owner-facing business settings flows for the active tenant
- registering tenant infrastructure in the master admin site

Current logging direction inside this app:

- prefer logging request-time tenant resolution and switching boundaries
- prefer logging owner-admin tenant runtime edges such as redirect or fallback behavior
- avoid logging pure membership policies, query helpers, or simple model accessors unless a concrete operational need appears

## Models

### `TenantModel`

`TenantModel` is the root business scope entity for the project.

Current fields cover:

- UUID primary key
- human-friendly tenant name
- unique slug
- optional business email
- optional support email
- optional phone number
- optional website URL
- active flag
- audit timestamps

Current intent:

- tenants should be introduced before domain apps start depending on them
- operational business contact data should live on `TenantModel`
- later domain models can reference `TenantModel` directly once multitenancy is wired through the rest of the project

Current examples of data that belong here:

- business contact channels
- support contact channels
- website links
- other non-visual business identity fields

### `TenantMembershipModel`

`TenantMembershipModel` links one user to one tenant.

Current fields cover:

- relation to `TenantModel`
- relation to `UserModel`
- membership role
- active flag
- primary-tenant flag
- audit timestamps

Current intent:

- a user may belong to multiple tenants
- each user should have at most one primary tenant membership
- tenant-specific roles should live on the membership rather than directly on the user model

### `TenantBrandingModel`

`TenantBrandingModel` stores reusable visual identity data for one tenant.

Current fields cover:

- relation to `TenantModel`
- optional display name
- light and dark logo variants
- light and dark icon variants
- light and dark favicon variants
- audit timestamps

Current intent:

- keep branding out of `TenantModel`
- reuse the same branding data across admin and future frontend surfaces
- let tenant-aware media storage place branding uploads under the active tenant path when one exists
- let the owner admin resolve light and dark favicon variants from branding, with final theme-specific selection handled by a small admin-side script
- keep this model focused on visual identity rather than operational contact data

Examples of data that should stay out of `TenantBrandingModel`:

- support email
- business email
- phone numbers
- website URLs

### `TenantGroupModel`

`TenantGroupModel` links one Django auth group to one tenant.

Current fields cover:

- relation to `TenantModel`
- relation to Django `Group`
- audit timestamps

Current intent:

- groups remain compatible with Django auth
- tenant ownership of groups stays explicit
- future owner-facing group visibility and assignment can be scoped by the active tenant

## Choices

The app keeps membership roles outside the model.

Current choice enum:

- `TenantRole`

Current values:

- `master`
- `owner`
- `operator`

## Use Cases

Current concrete use cases:

- attach users to one or more tenants
- attach Django groups to one tenant
- assign tenant roles such as `owner` and `operator` to support users
- choose the active tenant during owner-admin work
- display tenant-aware owner admin metadata such as title and header
- switch tenant context explicitly from the owner admin dropdown
- let active tenant owners update tenant branding from the owner admin business settings screen
- prefix uploaded media under `tenants/<tenant-slug>/...`

These are internal or admin-facing use cases.
The project does not yet expose a tenant-aware public frontend flow.

## Future Tenant Metadata Direction

The current base keeps the first operational contact fields on `TenantModel` and the visual identity fields on `TenantBrandingModel`.

Current rule of thumb:

- use `TenantModel` for business contact and operating metadata
- use `TenantBrandingModel` for display-oriented and asset-oriented metadata

Likely future additions when real business flows require them:

- `legal_name` on `TenantModel`
- `support_phone` on `TenantModel`
- tenant-specific sender metadata for outbound mail, potentially including a future verified `from_email`

Those fields remain future work because they require clearer product and deliverability rules than the current base structure needs.

Current mail-contact rule:

- `support_email` is the preferred tenant business contact channel
- `business_email` is the fallback business contact channel
- neither field should be treated as the authenticated technical mail sender by default

The mail-layer sender and reply policy is owned by:

- `docs/core/mail/runtime.md`

## Relationship With `accounts/`

`UserModel` keeps the authentication identity.

`tenancy/` adds tenant scope on top through:

- `TenantMembershipModel`
- `UserModel.tenants` using a through model

This keeps authentication and tenant membership related, but not collapsed into the same model.

## Admin

Current master registrations:

- `TenantModelAdmin`
- `TenantGroupModelAdmin`
- `TenantMembershipModelAdmin`

These registrations exist so the multitenancy base can be inspected and administered from the technical admin surface before the owner-facing tenant flows are defined.

The shared site classes and project admin wiring live in:

- `docs/core/adminsites/adminsites.md`

## Tests

The app already follows the project test structure convention.

Current test areas:

- `tenancy/tests/access/`
- `tenancy/tests/resolution/`
- `tenancy/tests/models/`
- `tenancy/tests/querysets/`
- `tenancy/tests/managers/`
- `tenancy/tests/middleware/`
- `tenancy/tests/views/`

## Related Docs

Use these documents together:

- `docs/tenancy/runtime.md`
  - request-time tenant context, switching, owner-admin runtime behavior
- `docs/tenancy/access.md`
  - tenant access policies and future policy direction for owner-managed apps
- `docs/tenancy/resolution.md`
  - detailed active-tenant strategy and resolver design

## What Should Live Here

Good candidates:

- tenant identity
- tenant membership rules
- tenant query helpers
- future tenant-scoped infrastructure that belongs to the multitenancy layer itself
- request-time tenancy infrastructure tightly coupled to tenant membership and active-tenant behavior

## What Should Not Live Here

Avoid placing app-specific domain logic in this app.

Examples:

- catalog business rules
- quotation lifecycle rules
- cart behavior
- project-wide admin infrastructure

Those concerns belong in:

- `docs/core/core.md`
- `docs/core/adminsites/adminsites.md`
