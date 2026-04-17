# Quotation App

This document explains the purpose and structure of the `quotation/` app.

## Goal

`quotation/` provides the quote request domain used by the project.

It currently defines:

- persisted quotes and quote item snapshots
- typed query infrastructure for quote data
- tenant-aware quote ownership at the quote root
- quotation-specific access rules for owner-managed flows
- DTOs and DTO factories for higher layers
- master admin registrations for technical visibility
- an owner-facing quotes flow for manual creation and follow-up

The app should remain focused on quote lifecycle and snapshot concerns.

## Current Structure

Current contents:

- `apps.py`
- `choices/`
- `models/`
- `dtos/`
- `admin/`
- `migrations/`
- `tests/`

## Responsibilities

The `quotation/` app is responsible for:

- defining persisted quote lifecycle data
- storing quote items as snapshots
- scoping quotes to the owning business
- exposing reusable quote query helpers
- exposing quotation-specific access rules
- registering quote admin flows for both master and owner admin sites

## Models

### `QuoteModel`

`QuoteModel` represents a formal quotation request.

Current fields cover:

- mandatory business ownership through `tenant`
- optional origin relations to cart and user
- internal workflow status
- customer and company information
- internal notes
- workflow timestamps
- audit timestamps

Related files:

- `quotation/models/quote_model.py`
- `quotation/models/querysets/quote_model_queryset.py`
- `quotation/models/managers/quote_model_manager.py`
- `quotation/access/quotation_access_policy.py`

### `QuoteItemModel`

`QuoteItemModel` stores a persisted snapshot of one item inside a quote.

Current snapshot fields cover:

- product and variant relations when they still exist
- product name snapshot
- SKU snapshot
- attribute snapshot
- unit price snapshot
- quantity
- notes
- creation timestamp

Current intent:

- quote items should preserve the commercial state used by the quote even if catalog data changes later
- quote items stay tenant-scoped through their parent `QuoteModel`

Related files:

- `quotation/models/quote_item_model.py`
- `quotation/models/querysets/quote_item_model_queryset.py`
- `quotation/models/managers/quote_item_model_manager.py`

## Choices

The app keeps quote lifecycle choices outside the model.

Current choice enum:

- `QuoteWorkflowStatus`

This keeps workflow values reusable across models, admins, and future services.

The choice labels are also translation-ready for owner-facing admin flows.

## DTOs

The app already includes DTOs and factories for decoupled consumption.

Current DTOs:

- `QuoteModelDTO`
- `QuoteItemModelDTO`

Current factories:

- `QuoteModelDTOFactory`
- `QuoteItemModelDTOFactory`

Current DTO direction:

- `QuoteModelDTO` includes `tenant_id` so higher layers can keep quote ownership explicit

## Admin

The app integrates with both shared admin site surfaces:

- `quotation/admin/master/`
- `quotation/admin/owner/`

### Master Admin

The master admin keeps quotes and quote items visible as raw technical entities.

Current registrations:

- `QuoteModelAdmin`
- `QuoteItemModelAdmin`

### Owner Admin

The owner admin exposes a curated `Sales > Quotes` flow.

Current behavior:

- the owner manages `QuoteModel` as the main entity
- the owner quote queryset is scoped to the active tenant
- quote items appear as a top-level inline tab beside the general quote form
- the add flow supports manual quote creation with items
- the change flow freezes quote items as snapshots
- destructive delete is disabled for quotes

Current owner-specific pieces:

- `QuoteModelAdmin`
- `QuoteItemModelInline`
- `QuoteItemModelInlineForm`
- `QuoteItemModelInlineFormSet`
- `QuotationAccessPolicy`

Current owner workflow:

- on add:
  - the owner can create a quote manually
  - the quote inherits `request.tenant`
  - the owner can add quote items inline
  - the owner must provide a customer name plus at least one contact channel
  - product and variant choices are limited to the active tenant catalog
  - snapshot fields are populated automatically from the selected product and optional variant
- on change:
  - quote items become read-only snapshots
  - origin and timeline information become visible

### Access Policy

`quotation/` now defines one app-specific access policy:

- `QuotationAccessPolicy`

Current direction:

- quotation is operator-capable rather than owner-only
- access builds on active-tenant membership plus Django permissions
- object-level checks confirm that a quote or quote item belongs to the active tenant context

This keeps sidebar visibility, owner admin permissions, and future quotation-specific checks aligned around one reusable rule set.

### Logging

`quotation/` now applies the shared logging rollout at the owner-admin runtime boundaries that matter operationally.

Current logging boundaries:

- `QuoteModelAdmin.get_queryset()`
- `QuoteModelAdmin.save_model()`
- `QuoteItemModelInlineFormSet.save_new()`

Current direction:

- log tenant-scoped queryset resolution
- log owner quote saves
- log quote item snapshot creation
- keep logging out of pure models and queryset internals

### Translation

The quotation owner flow is now prepared for the project translation workflow.

Current translation-ready pieces:

- `QuotationConfig.verbose_name`
- quote model and quote item model labels and help texts
- quote workflow status choice labels
- owner quote admin fieldset titles and descriptions
- owner quote form labels, help texts, and validation errors
- owner quote item inline labels, help texts, and validation errors

## Status and Timestamp Direction

The current owner admin allows the workflow field to be edited directly while workflow timestamps remain read-only.

Current behavior:

- `workflow_status` is owner-editable
- `requested_at` and `resolved_at` are read-only
- `requested_at` is derived the first time the workflow reaches `requested` or beyond
- `resolved_at` is derived the first time the workflow reaches `completed` or `cancelled`
- workflow transitions cannot move backward once the quote progresses

Future direction:

- keep the internal workflow focused on `draft`, `requested`, `in_progress`, `completed`, and `cancelled`
- keep any future `customer_status` as a second later dimension instead of overloading `workflow_status`
- only add customer-facing timestamps such as `sent_at` or `answered_at` once a real customer-facing quote flow exists

For the target lifecycle design, see:

- `docs/quotation/lifecycle.md`

## Tests

The app already follows the project test structure convention.

Current test areas:

- `quotation/tests/models/`
- `quotation/tests/managers/`
- `quotation/tests/querysets/`
- `quotation/tests/access/`
- `quotation/tests/admin/`
- `quotation/tests/dtos/`
- `quotation/tests/factories/`

Project-level admin behavior tied to `quotation` currently lives in:

- `core/tests/adminsites/`

## What Should Live Here

Good candidates:

- quote lifecycle rules
- quote snapshot rules
- quote query helpers
- quote DTOs and DTO factories
- quotation-specific admin implementations

## What Should Not Live Here

Avoid placing unrelated project infrastructure in this app.

Examples:

- project admin site wiring
- global Unfold settings infrastructure
- catalog persistence rules
- storage configuration
