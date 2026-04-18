# Owner-Managed Apps

This document explains the default wiring pattern for future owner-managed apps inside the owner admin.

See also:

- `docs/project.md`
- `docs/core/core.md`
- `docs/core/adminsites/adminsites.md`
- `docs/tenancy/access.md`
- `docs/accounts/accounts.md`

## Goal

This guide exists to keep future owner-managed apps aligned with the current owner-admin structure without forcing each new domain to invent its own access and wiring rules.

It should help answer:

- when one app should stay owner-only
- when one app may allow active tenant members such as `operator`
- how owner-admin querysets, forms, permissions, and sidebar visibility should align

## Surface Categories

The current base structure already separates two categories of owner-admin surfaces:

- owner-only surfaces such as `accounts` and `tenancy`
- tenant-member surfaces that future apps may expose to active tenant members when Django permissions allow it

Future apps should not copy the `accounts` rule set blindly.

`accounts` stays stricter because it manages support users, tenant memberships, and tenant-scoped permission groups.

## Default Wiring Rule

The intended default wiring rule for future owner-managed apps is:

1. require active-tenant membership through `TenantAccessPolicy.can_access_tenant(...)`
2. combine that tenant-membership check with standard Django permissions such as `view`, `change`, `add`, or `delete`
3. scope querysets, forms, and group assignment to the active tenant
4. keep `accounts` and `tenancy` owner-only unless their product scope changes explicitly

This keeps tenant-aware operator flows possible without turning every future app into an owner-only surface.

## Wiring Checklist For New Owner-Managed Apps

When a new tenant-aware app is added to the owner admin:

- register the app in the owner admin site
- filter all owner-admin querysets to the active tenant
- use `TenantAccessPolicy.can_access_tenant(...)` as the base tenant-scope check for operator-capable apps
- combine the base tenant-scope check with `request.user.has_perm(...)` for module, view, change, add, and delete access
- keep owner-only apps on `TenantAccessPolicy.can_manage_tenant(...)`
- add sidebar items only when the same access rule used by the admin surface passes

## Relationship With `accounts/`

`accounts/` is intentionally stricter than the default future-app pattern.

It remains owner-only because it manages:

- support users
- tenant memberships
- tenant-scoped permission groups

That makes `accounts` a bad template for lighter operator-capable business apps.

## Relationship With `tenancy/access/`

The reusable authorization base for future owner-managed apps should stay in `tenancy/access/`.

Current direction:

- `TenantAccessPolicy` stays as the reusable tenant-membership and tenant-role base policy
- app-specific policies should only appear when one domain needs stricter rules than the generic tenant-member plus Django-permission pattern

## What This Document Does Not Own

This document does not own:

- shared admin-site infrastructure
- Unfold site integration details
- runtime active-tenant resolution
- request-time tenant switching behavior

Those concerns are documented in:

- `docs/core/adminsites/adminsites.md`
- `docs/tenancy/runtime.md`
- `docs/tenancy/resolution.md`
