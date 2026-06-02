# Masterdata App

This document explains the purpose and structure of the `masterdata/` app.

## Goal

`masterdata/` provides tenant-owned business reference data used by other domain apps.

It currently defines:

- persisted brands and categories
- typed query infrastructure for brand and category data
- tenant-aware ownership at the reference-data root
- brand-specific and category-specific access rules for owner-managed flows
- DTOs and DTO factories for higher layers
- master admin registrations for technical visibility
- owner-facing brand and category flows for active-tenant business management

The app should remain focused on business reference data and should not absorb product-specific or project-wide infrastructure concerns.

## Current Structure

Current contents:

- `apps.py`
- `models/`
- `dtos/`
- `admin/`
- `migrations/`
- `static/`
- `tests/`

## Responsibilities

The `masterdata/` app is responsible for:

- defining tenant-owned reference-data persistence models
- exposing reusable brand and category query helpers
- keeping category hierarchies tenant-scoped and cycle-free
- exposing brand-specific and category-specific access rules
- exposing DTOs for higher layers that should not depend directly on ORM objects
- registering masterdata admin flows for both master and owner admin sites

## Models

### `BrandModel`

`BrandModel` represents one reusable business-owned brand reference.

Current fields cover:

- mandatory business ownership through `tenant`
- brand naming and slug
- optional internal description
- active flag
- audit timestamps

Current tenant-aware rules:

- every brand belongs to one `TenantModel`
- slug uniqueness is scoped per tenant instead of globally
- owner-admin brand query boundaries start from the active tenant

Current admin-facing metadata direction:

- brand fields expose user-friendly `verbose_name` and `help_text` metadata
- those labels and help texts are translation-ready for owner-admin usage

Related files:

- `masterdata/models/brand_model.py`
- `masterdata/models/querysets/brand_model_queryset.py`
- `masterdata/models/managers/brand_model_manager.py`
- `masterdata/access/brand_access_policy.py`

### `CategoryModel`

`CategoryModel` represents one reusable business-owned category reference.

Current fields cover:

- mandatory business ownership through `tenant`
- category naming and slug
- optional internal description
- optional public banner image for storefront category surfaces
- optional self-referential parent
- manual ordering
- active flag
- optional featured flag for curated storefront placement
- audit timestamps

Current hierarchy rules:

- every category belongs to one `TenantModel`
- slug uniqueness is scoped per tenant instead of globally
- category display names may repeat, including similarly named subcategories under different roots
- repeated category names must still use different slugs inside the same tenant
- parent categories must belong to the same tenant
- a category cannot parent itself
- category trees cannot contain cycles

Current owner-admin direction:

- the category changelist is focused on root categories
- parent choices are scoped to the active tenant
- current and descendant categories are excluded from parent choices on change views
- direct child categories can be created inline from the category screen
- the add flow can persist one parented category together with inline child categories in one submission
- duplicate subcategory names are allowed when each category keeps a tenant-unique URL slug
- duplicate slugs are reported as owner-facing slug field errors before saving
- the owner category form exposes a local slug suggestion helper through `core.forms.ActionInputWidget`
- root category suggestions use the category name, while child suggestions prefix the parent slug
- duplicate slug suggestions receive incremental suffixes such as `-2` or `-3`
- categories can expose one optional banner image for future public category pages
- categories can be curated explicitly through `is_featured` for future storefront sections
- the category screen separates core details, storefront presentation, and catalog organization into distinct sections

Current admin-facing metadata direction:

- category fields expose user-friendly `verbose_name` and `help_text` metadata
- those labels, help texts, and validation errors are translation-ready for owner-admin usage

Related files:

- `masterdata/models/category_model.py`
- `masterdata/models/querysets/category_model_queryset.py`
- `masterdata/models/managers/category_model_manager.py`
- `masterdata/access/category_access_policy.py`

## QuerySets and Managers

The app follows the project rule of keeping reusable filtering logic in querysets and exposing typed entrypoints through managers.

Current helpers:

- `BrandModelQuerySet.active()`
- `BrandModelQuerySet.for_tenant(tenant)`
- `CategoryModelQuerySet.active()`
- `CategoryModelQuerySet.roots()`
- `CategoryModelQuerySet.children_of(parent)`
- `CategoryModelQuerySet.for_tenant(tenant)`

Current tenant-aware query direction:

- brands expose `for_tenant(tenant)` directly
- categories expose `for_tenant(tenant)` directly
- category tree navigation stays inside one tenant boundary

## DTOs

The app already includes DTOs and factories for decoupled consumption.

Current DTOs:

- `BrandModelDTO`
- `CategoryModelDTO`

Current factories:

- `BrandModelDTOFactory`
- `CategoryModelDTOFactory`

Current DTO direction:

- both DTOs include `tenant_id` so higher layers can keep ownership explicit
- category DTOs also expose `banner_name` and `is_featured` for future storefront assembly

## Admin

The app integrates with both shared admin site surfaces:

- `masterdata/admin/master/`
- `masterdata/admin/owner/`

### Master Admin

The master admin keeps raw brand and category entities visible for full technical administration.

Current registrations:

- `BrandModelAdmin`
- `CategoryModelAdmin`

### Owner Admin

The owner admin exposes curated reference-data flows inside the `Catalog` sidebar group.

Current behavior:

- brands and categories are scoped to the active tenant
- the owner flow is operator-capable rather than owner-only
- category parent choices are limited to valid in-tenant options
- direct child categories can be created and edited inline
- destructive delete is disabled for both brands and categories

Current owner-specific pieces:

- `BrandAccessPolicy`
- `CategoryAccessPolicy`
- `BrandModelAdmin`
- `BrandModelAdminForm`
- `CategoryModelAdmin`
- `CategoryModelAdminForm`
- `CategoryChildModelInline`
- `CategoryChildModelInlineForm`
- `CategoryChildModelInlineFormSet`
- local CSS for small owner-specific layout corrections

Current navigation decision:

- `Brands` and `Categories` currently stay under the `Catalog` sidebar group
- this is intentional because the current owner mental model is still "catalog support data"
- if `masterdata/` grows beyond brand and category, a dedicated sidebar group can be reconsidered later

## Access Policies

`masterdata/` now defines two app-specific access policies:

- `BrandAccessPolicy`
- `CategoryAccessPolicy`

Current direction:

- masterdata is operator-capable rather than owner-only
- access builds on active-tenant membership plus Django permissions
- object-level checks confirm that one brand or category belongs to the active tenant context

This keeps sidebar visibility, owner admin permissions, and future reference-data checks aligned around reusable rule sets without collapsing everything into one generic policy file.

## Logging

`masterdata/` now applies the shared logging rollout at the owner-admin runtime boundaries that matter operationally.

Current logging boundaries:

- `BrandModelAdmin.get_queryset()`
- `BrandModelAdmin.save_model()`
- `CategoryModelAdmin.get_queryset()`
- `CategoryModelAdmin.save_model()`
- `CategoryChildModelInlineFormSet.save_new()`

Current direction:

- log tenant-scoped queryset resolution
- log owner brand and category saves
- log inline child-category creation
- keep logging out of pure models and queryset internals

## Translation

The masterdata owner flow is now prepared for the project translation workflow.

Current translation-ready pieces:

- `MasterdataConfig.verbose_name`
- brand model and category model labels and help texts
- category hierarchy validation errors
- owner brand admin fieldset titles and descriptions
- owner brand form labels and help texts
- owner category admin fieldset titles and descriptions
- owner category form labels and help texts
- child-category inline labels and help texts

## Relationship To Catalog

`masterdata/` is intentionally separate from `catalog/`.

Current rationale:

- `catalog/` owns product aggregates and product-specific operational content
- `masterdata/` owns reusable business reference data consumed by catalog
- `BrandModel` and `CategoryModel` are reference data, not product-internal row details

That is why entities such as `ProductImageModel` remain in `catalog/`, while brand and category references stay in `masterdata/`.

## Tests

The app already follows the project test structure convention.

Current test areas:

- `masterdata/tests/models/`
- `masterdata/tests/managers/`
- `masterdata/tests/querysets/`
- `masterdata/tests/access/`
- `masterdata/tests/admin/`
- `masterdata/tests/dtos/`
- `masterdata/tests/factories/`

Project-level admin behavior tied to `masterdata` currently lives in:

- `core/tests/adminsites/`

## What Should Live Here

Good candidates:

- brand and category persistence rules
- reference-data query helpers
- brand-specific and category-specific access rules
- reference-data DTOs and DTO factories
- masterdata-specific admin implementations
- future tenant-owned business reference-data services

## What Should Not Live Here

Avoid placing unrelated project infrastructure or product-aggregate content in this app.

Examples:

- project admin site wiring
- global Unfold settings infrastructure
- product image persistence
- quote snapshot rules
- storage configuration
