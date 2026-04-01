# Admin Sites

This document explains the purpose and structure of `core/adminsites/`.

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

### `unfold/`

Contains the adapter layer between the custom admin sites and Unfold settings.

This package should keep two responsibilities clearly separated:

- `AdminSiteUnfoldSettings`: builds the static settings dictionary for one namespace
- `AdminSiteUnfoldCallbacks`: resolves the current site instance from the request and serves runtime callbacks

It should not become a second source of truth for site identity.

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
- `catalog/admin/owner/`

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
