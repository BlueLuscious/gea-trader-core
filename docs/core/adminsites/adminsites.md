# Admin Sites

This document explains the purpose and structure of `core/adminsites/`.

See also:

- `docs/project.md`
- `docs/core/core.md`
- `docs/accounts/accounts.md`
- `docs/tenancy/tenancy.md`
- `docs/tenancy/runtime.md`
- `docs/tenancy/access.md`
- `docs/core/adminsites/owner-managed-apps.md`

## Goal

`core/adminsites/` contains project-level admin infrastructure shared across apps.

It exists to define:

- custom `AdminSite` classes
- admin site namespaces
- shared admin site instances
- the Unfold integration layer used by those sites

The package should stay focused on project-wide admin infrastructure, not domain-specific admin implementations.

## Current Structure

Current contents:

- `admin_namespace.py`
- `registry.py`
- `site_instances.py`
- `sites/`
- `services/`
- `unfold/`

## Responsibilities

### `admin_namespace.py`

Defines the project admin namespaces used for routing and site resolution.

Current namespaces:

- `master_admin`
- `owner_admin`

### `registry.py`

Maps each admin namespace to its corresponding admin site class and site instance.

Use this registry for namespace-based site resolution instead of hardcoding imports inside the Unfold adapter.

This registry is project admin infrastructure. It should not contain Unfold-specific behavior.

### `site_instances.py`

Creates the concrete shared admin site instances used by:

- `core/urls.py`
- admin registration modules

These instances are the actual Django admin site objects exposed by the project.

### `sites/`

Contains the admin site class hierarchy.

Current site classes:

- `BaseAdminSite`
- `MasterAdminSite`
- `OwnerAdminSite`

Rules:

- keep one principal class per file
- keep shared default behavior in the base site
- let concrete sites override hooks rather than duplicating wiring
- keep metadata getters at class level when they only expose site identity
- prefer instance methods for hooks that depend on the real admin site runtime state such as app registry, app list, or per-instance navigation

### `services/`

Contains small admin-infrastructure services used by site classes.

Current services include:

- active-tenant switch URL building
- owner tenant dropdown building
- owner tenant branding resolution
- owner tenant sidebar navigation building

Rules:

- keep request-aware helper logic here when it does not belong in the ORM model itself
- avoid pushing Unfold-specific payload shaping into unrelated domain models
- keep site classes focused on metadata hooks and admin behavior orchestration
- prefer logging request-aware fallback and builder boundaries here instead of inside trivial site metadata getters

### `unfold/`

Contains the adapter layer between the custom admin sites and Unfold settings.

This package should keep two responsibilities clearly separated:

- `AdminSiteUnfoldSettings`: builds the static settings dictionary for one namespace
- `AdminSiteUnfoldCallbacks`: resolves the current site instance from the request and serves runtime callbacks

It should not become a second source of truth for site identity.

### Import/Export Integration

The project uses `django-import-export` through Unfold's integration package for owner-admin data import and export flows.

Base integration lives in project settings:

- `unfold.contrib.import_export`
- `import_export`

Rules:

- keep the dependency and installed-app wiring in the base project layer
- keep model-specific resources inside the app that owns the model
- prefer app-owned resources such as `<app>/resources/`
- base-owned examples should use base apps such as `accounts/resources/` or `tenancy/resources/`
- use Unfold's import/export forms when an admin class enables import/export
- do not create project-wide custom import/export templates unless the Unfold integration has a real gap
- keep imports tenant-scoped in owner admin and never trust tenant identifiers from uploaded files
- start with synchronous admin preview/dry-run imports before introducing asynchronous import jobs
- use asynchronous imports only when file size, image downloads, progress reporting, or retry behavior justify the extra runtime state

## Design Rules

The source of truth for site identity should remain the site classes themselves.

Examples:

- `site_title`
- `site_header`
- `site_symbol`
- `site_url`
- per-site sidebar hooks

The Unfold layer should adapt those values, not redefine them independently.

Bootstrap and runtime should stay separated:

- bootstrap: build the Unfold settings dictionary for each namespace
- runtime: resolve the current site instance from the request and delegate request-aware hooks

## Relationship With App Admins

`core/adminsites/` should define the shared admin infrastructure only.

App-specific admin implementations should live in their respective apps.

Recommended structure:

```text
<app>/admin/
  master/
  owner/
```

Examples:

- `accounts/admin/master/`
- `tenancy/admin/owner/`
- `tenancy/admin/master/`

This keeps:

- site infrastructure in `core`
- domain admin logic close to each app

## Current Behavior

### `MasterAdminSite`

Intended for technical platform administrators.

Characteristics:

- active superusers only
- full Django-style admin visibility
- custom master sidebar navigation

### `OwnerAdminSite`

Intended for business owners and operators.

Characteristics:

- active staff users
- guided domain-specific admin experience
- simpler navigation than the master site
- tenant-aware metadata such as title and header when an active tenant is resolved
- compatible with explicit active-tenant switching backed by session state
- tenant switcher dropdown in the site header when the user belongs to multiple active tenants
- tenant branding-aware title, header, logo, icon, and favicons through a dedicated adminsite service
- callable Unfold asset settings such as `SCRIPTS` and `STYLES` are resolved through the shared `BaseAdminSite` adapter so request-aware asset hooks actually reach the rendered template context
- `Business -> Settings` links directly to the native tenant-scoped `TenantModel` change form with owner-admin helper classes from `tenancy/admin/owner/`
- tenant switching keeps the tenant settings screen tenant-aware and falls back from other admin change screens to portable destinations
- owner favicon light and dark variants are finalized with one small admin script because upstream Unfold does not expose a narrow template hook for favicon `media` attributes
- custom language switching endpoint from `core/i18n/` used by the Unfold language selector to keep the default language unprefixed
- owner sidebar entries are curated instead of mirroring the full Django app list
- the current `Accounts` navigation is intentionally owner-only even inside the owner admin site
- curated navigation instead of raw app exposure
- model access should rely on standard Django permissions and groups
- hard delete should be avoided where the model already exposes an active/inactive state
- owner flows should stay app-specific and can use app-local forms, inlines, formsets, and CSS when that improves the guided experience
- app-specific visual fixes should stay local to the app instead of patching Unfold globally

Current example:

- curated owner flows currently live in:
  - `catalog/admin/owner/`
  - `quotation/admin/owner/`

See:

- `docs/catalog/catalog.md`

### Owner Group Convention

The current recommended convention is to create an `OwnerAdmins` group from the Django admin and assign the permissions required by the owner flows manually while those flows are still evolving.

The exact permissions should be documented by the app that owns each owner flow.

Current example:

- `docs/catalog/catalog.md`

## Maintenance Rule

If a concern is shared by all admin sites, place it in:

- `sites/base_admin_site.py`
- or the `unfold/` adapter layer when it is Unfold-specific

If a concern is specific to one domain app, keep it inside that app instead of growing `core/adminsites/`.

App docs should describe only their own registrations and then link back here for shared site infrastructure.

The future wiring pattern for new owner-managed apps is documented separately in:

- `docs/core/adminsites/owner-managed-apps.md`
