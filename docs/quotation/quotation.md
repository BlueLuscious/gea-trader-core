# Quotation App

This document explains the purpose and structure of the `quotation/` app.

## Goal

`quotation/` provides the quote request domain used by the project.

It currently defines:

- persisted quotes and quote item snapshots
- typed query infrastructure for quote data
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
- exposing reusable quote query helpers
- registering quote admin flows for both master and owner admin sites

## Models

### `QuoteModel`

`QuoteModel` represents a formal quotation request.

Current fields cover:

- optional origin relations to cart and user
- lifecycle status
- customer and company information
- internal notes
- quote lifecycle timestamps
- audit timestamps

Related files:

- `quotation/models/quote_model.py`
- `quotation/models/querysets/quote_model_queryset.py`
- `quotation/models/managers/quote_model_manager.py`

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

Related files:

- `quotation/models/quote_item_model.py`
- `quotation/models/querysets/quote_item_model_queryset.py`
- `quotation/models/managers/quote_item_model_manager.py`

## Choices

The app keeps quote lifecycle choices outside the model.

Current choice enum:

- `QuoteStatus`

This keeps status values reusable across models, admins, and future services.

## DTOs

The app already includes DTOs and factories for decoupled consumption.

Current DTOs:

- `QuoteModelDTO`
- `QuoteItemModelDTO`

Current factories:

- `QuoteModelDTOFactory`
- `QuoteItemModelDTOFactory`

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
- quote items appear as a top-level inline tab beside the general quote form
- the add flow supports manual quote creation with items
- the change flow freezes quote items as snapshots
- destructive delete is disabled for quotes

Current owner-specific pieces:

- `QuoteModelAdmin`
- `QuoteItemModelInline`
- `QuoteItemModelInlineForm`
- `QuoteItemModelInlineFormSet`

Current owner workflow:

- on add:
  - the owner can create a quote manually
  - the owner can add quote items inline
  - the owner must provide a customer name plus at least one contact channel
  - snapshot fields are populated automatically from the selected product and optional variant
- on change:
  - quote items become read-only snapshots
  - origin and timeline information become visible

## Status and Timestamp Direction

The current owner admin allows the status field to be edited directly while lifecycle timestamps remain read-only.

Current behavior:

- `status` is owner-editable
- `requested_at`, `sent_at`, and `answered_at` are read-only
- those timestamps are not yet auto-derived from status transitions

Future direction:

- status transitions should eventually drive lifecycle timestamps consistently
- that logic should live in domain or application rules, not in ad hoc admin-side field editing

## Tests

The app already follows the project test structure convention.

Current test areas:

- `quotation/tests/models/`
- `quotation/tests/managers/`
- `quotation/tests/querysets/`
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
