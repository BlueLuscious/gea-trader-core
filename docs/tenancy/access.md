# Tenancy Access

This document explains the tenant-scoped access policies owned by `tenancy/`.

See also:

- `docs/project.md`
- `docs/tenancy/tenancy.md`
- `docs/core/adminsites/adminsites.md`
- `docs/core/adminsites/owner-managed-apps.md`
- `docs/accounts/accounts.md`

## Goal

The access layer exists to keep tenant membership and tenant-scoped authorization rules explicit and reusable.

It should:

- centralize tenant membership checks
- centralize tenant role checks
- support owner-only flows where required
- give future apps one reusable base policy instead of ad hoc role checks

## Current Policy Split

`tenancy/access/` currently separates tenant authorization into small policy objects.

Current policies:

- `TenantAccessPolicy`
- `AccountsAccessPolicy`

## `TenantAccessPolicy`

This is the base policy for tenant membership and role checks.

Current responsibilities:

- verify whether a user belongs to one tenant
- verify whether a user has one tenant role
- verify whether a user may manage a tenant as an active `owner`

This policy should stay generic and reusable across apps that need tenant membership checks.

## `AccountsAccessPolicy`

This is the `accounts/`-specific policy now owned by `accounts/`.

Current responsibilities:

- verify whether the current request may manage owner-scoped accounts
- decide whether one user is visible inside owner `Users`
- decide whether one group is visible inside owner `Groups`

This keeps the reusable tenant-role checks in the base tenancy policy while moving `accounts`-specific authorization into the `accounts/` domain that actually consumes it.

## Policy Direction For Future Apps

The current policy split is intended to scale in two layers:

- `TenantAccessPolicy` stays as the reusable tenant-membership and tenant-role base policy
- app-specific policies should sit on top only when one domain needs stricter rules than the generic tenant-member flow

Current architectural direction:

- `accounts` and `tenancy` remain owner-only surfaces
- future owner-managed apps may allow active tenant members such as `operator` to access the app when they both:
  - belong to the active tenant
  - hold the required Django permissions through tenant-scoped groups or direct user permissions

This means `TenantAccessPolicy` remains the base reusable policy layer, while future app-specific policies should only appear when one domain needs stricter rules than the generic tenant-member plus Django-permission pattern.

For the concrete owner-admin wiring checklist for future apps, see:

- `docs/core/adminsites/owner-managed-apps.md`

## Relationship With `accounts/`

`accounts/` consumes tenant authorization through these two layers:

- `TenantAccessPolicy` for base tenant-membership and role checks
- `AccountsAccessPolicy` for `accounts`-specific visibility and management rules

This stricter owner-only rule is intentional for `accounts`.

Future tenant-aware apps should not copy the `accounts` flow by default.
`accounts` stays stricter because it manages support users, memberships, and tenant-scoped permission groups.

## Current Logging Direction

The access layer should stay relatively quiet.

Current direction:

- prefer logging runtime boundaries that consume access outcomes instead of logging every policy decision
- only add policy-level logs when one real operational blind spot appears

This keeps the access layer reusable without turning every permission check into console noise.

## What Should Live Here

Good candidates:

- reusable tenant membership checks
- reusable tenant role checks
- small app-specific tenant access policies when one app truly needs stricter rules than the base flow

## What Should Not Live Here

Avoid placing these here:

- request-time tenant resolution logic
- session switching logic
- owner-admin infrastructure rules that belong in `core/adminsites/`

Those concerns belong in:

- `docs/tenancy/runtime.md`
- `docs/tenancy/resolution.md`
- `docs/core/adminsites/adminsites.md`
