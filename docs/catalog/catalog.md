# Catalog App

This document explains the purpose and structure of the `catalog/` app.

## Goal

`catalog/` provides the product catalog domain used by the project.

It currently defines:

- the core catalog models
- typed query infrastructure for those models
- DTOs and DTO factories for decoupled consumption
- a catalog-specific tenant-aware access policy
- master admin registrations for technical administration
- an owner-focused products flow inside the curated owner admin

The app should remain focused on product catalog concerns and not absorb project-wide infrastructure that belongs in `core/`.

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

The `catalog/` app is responsible for:

- defining catalog persistence models
- exposing reusable catalog query helpers through querysets and managers
- keeping catalog ownership tenant-aware from the product root
- exposing catalog-specific access rules for owner-managed catalog flows
- exposing DTOs for higher layers that should not depend directly on ORM objects
- registering catalog admin flows in both `master` and `owner` admin surfaces

## Models

### `ProductModel`

`ProductModel` is the public catalog entity.

Current fields cover:

- tenant ownership
- brand and category relations
- customer-facing naming and description
- catalog visibility flags
- quote-flow behavior
- audit timestamps

Current intent:

- the product is the main catalog entity shown to users
- the product is the tenant-owned root of the catalog aggregate
- product variants represent concrete sellable or quotable options attached to that product

Current tenant-aware rules:

- every product belongs to one `TenantModel`
- slug uniqueness is scoped per tenant instead of globally
- owner-admin catalog query boundaries start from the product tenant

Current admin-facing metadata direction:

- product fields expose user-friendly `verbose_name` and `help_text` metadata
- those labels and help texts are translation-ready for owner-admin usage

Related files:

- `catalog/models/product_model.py`
- `catalog/models/querysets/product_model_queryset.py`
- `catalog/models/managers/product_model_manager.py`

### `ProductVariantModel`

`ProductVariantModel` represents a concrete variation of a product.

Current fields cover:

- relation to `ProductModel`
- variant naming and SKU
- free-form `attributes_json`
- optional price
- default flag
- active flag
- manual ordering
- audit timestamps

Current behavior:

- only one default variant is allowed per product
- variants are the current place where price lives
- variants are used as the more concrete commercial layer for quoting or selling
- variant fields expose user-friendly labels and help texts for admin translation flows

Related files:

- `catalog/models/product_variant_model.py`
- `catalog/models/querysets/product_variant_model_queryset.py`
- `catalog/models/managers/product_variant_model_manager.py`

### `ProductImageModel`

`ProductImageModel` stores images attached to a product or to one of its variants.

Current fields cover:

- relation to `ProductModel`
- optional relation to `ProductVariantModel`
- image file
- alt text
- primary-image flag
- manual ordering
- creation timestamp

Current metadata direction:

- image fields expose user-friendly labels and help texts for owner-admin usage

Related files:

- `catalog/models/product_image_model.py`
- `catalog/models/querysets/product_image_model_queryset.py`
- `catalog/models/managers/product_image_model_manager.py`

## QuerySets and Managers

The app follows the project rule of keeping reusable filtering logic in querysets and exposing typed entrypoints through managers.

Current product helpers:

- `active()`
- `featured()`
- `requiring_quote()`
- `with_related()`

Current variant helpers:

- `active()`
- `defaults()`
- `for_tenant(tenant)`
- `for_product(product)`

Current image helpers:

- `primary()`
- `ordered()`
- `for_tenant(tenant)`

Current tenant-aware query direction:

- products expose `for_tenant(tenant)` directly
- variants and images stay tenant-scoped through `product__tenant`

This keeps common catalog queries out of views, templates, and admin code.

## DTOs

The app already includes DTOs and factories for decoupled consumption.

Current DTOs:

- `ProductModelDTO`
- `ProductVariantModelDTO`
- `ProductImageModelDTO`

Current factories:

- `ProductModelDTOFactory`
- `ProductVariantModelDTOFactory`
- `ProductImageModelDTOFactory`

Current note:

- the DTO layer is still intentionally lean
- it mirrors the persistence structure closely
- more presentation-specific DTOs can be added later when the public catalog surface becomes more concrete

## Admin

The app integrates with both shared admin site surfaces:

- `catalog/admin/master/`
- `catalog/admin/owner/`

### Master Admin

The master admin keeps the raw technical catalog entities visible for full administration.

Current registrations:

- `ProductModelAdmin`
- `ProductVariantModelAdmin`
- `ProductImageModelAdmin`

Characteristics:

- technical visibility
- full model-oriented administration
- autocomplete fields where relations are important

### Owner Admin

The owner admin exposes a curated `Catalog > Products` flow.

Current behavior:

- the owner works from `ProductModel` as the main entrypoint
- the flow is tenant-scoped to the active tenant
- the flow is operator-capable rather than owner-only
- variants and images are edited inline from the same screen
- the form is grouped with Unfold tabs for a more guided layout
- destructive delete is avoided where the model already exposes state through `is_active`

Current owner-specific pieces:

- `CatalogAccessPolicy`
- `ProductModelAdmin`
- `ProductModelAdminForm`
- `ProductVariantModelInline`
- `ProductImageModelInline`
- `ProductImageModelInlineFormSet`
- local CSS for small owner-specific layout corrections

Current UX decisions:

- `ProductVariantModelInline` stays tabular because variants behave like row data
- `ProductImageModelInline` is stacked because images benefit from a more card-like layout
- image inline variant choices are restricted to variants of the current product
- fieldsets are grouped into business-friendly sections instead of exposing a raw model form

Current access direction:

- the owner sidebar and the owner product admin both rely on `CatalogAccessPolicy`
- the base gate is active-tenant membership through `TenantAccessPolicy.can_access_tenant(...)`
- Django permissions such as `catalog.view_productmodel` and `catalog.change_productmodel` stay as the operation-specific layer
- product objects outside the active tenant are intentionally hidden from the owner flow

Current runtime logging direction:

- the owner product admin logs tenant-scoped queryset resolution
- the owner product admin logs product saves
- the image inline formset logs variant choice construction for the current product
- models and query helpers stay quiet

## Current Domain Direction

The current catalog direction is:

- `ProductModel` is the entity users browse
- `ProductVariantModel` is the concrete selectable option behind that product

This means the public catalog should likely render products as the main cards and detail pages, while variants resolve concrete pricing and selection behavior behind the scenes.

Open decision still under discussion:

- whether products with uniform pricing should continue to rely only on variants
- or whether a shared product-level base price should exist to avoid repeating the same value across many variants

No product-level base price has been introduced yet.

## Tests

The app already follows the project test structure convention.

Current test areas:

- `catalog/tests/models/`
- `catalog/tests/managers/`
- `catalog/tests/querysets/`
- `catalog/tests/dtos/`
- `catalog/tests/factories/`

Project-level admin behavior tied to `catalog` currently lives in:

- `core/tests/adminsites/`

This split is intentional:

- domain model/query behavior stays in the app
- shared adminsite infrastructure behavior stays in `core/tests/`

## What Should Live Here

Good candidates:

- catalog persistence rules
- catalog query helpers
- catalog access policy rules
- catalog DTOs and DTO factories
- catalog-specific admin implementations
- future catalog services or presentation mappers

## What Should Not Live Here

Avoid putting project-wide platform concerns in this app.

Examples:

- project admin site wiring
- project-wide Unfold settings infrastructure
- global storage configuration
- unrelated account or quotation platform infrastructure
