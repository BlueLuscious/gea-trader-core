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
- factories for domain snapshot assembly
- services for cart-origin quote conversion and tenant notifications
- services for internal workflow transitions
- master admin registrations for technical visibility
- an owner-facing quotes flow for manual creation and follow-up

The app should remain focused on quote lifecycle and snapshot concerns.

## Current Structure

Current contents:

- `apps.py`
- `choices/`
- `models/`
- `factories/`
- `dtos/`
- `services/`
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
- converting eligible runtime carts into quote requests
- notifying the tenant when one public quote request is accepted
- registering quote admin flows for both master and owner admin sites

## Public Cart-To-Quote Runtime

The public cart-to-quote flow is orchestrated by `quotation/services/`.
The storefront HTTP endpoint lives in `front/`, but quotation owns the quote-domain side effects.

Current service boundaries:

- `CartQuoteRequestService`: orchestrates conversion, notification dispatch, and result DTO assembly.
- `CartQuoteRequestConverter`: converts one active cart into a requested quote and persisted quote-item snapshots.
- `CartQuoteRequestNotificationDispatcher`: resolves tenant recipients and dispatches the notification through the shared mail service.
- `CartQuoteRequestNotificationBuilder`: builds the mail request and context for one quote notification.
- `QuoteAdminUrlBuilder`: builds the owner-admin quote URL used in notifications.
- `QuoteWorkflowTransitionService`: transitions quotes through internal workflow actions and keeps the future event hook outside admin code.

Current factory boundary:

- `QuoteItemSnapshotFactory`: builds `QuoteItemModel` snapshot instances from cart items before bulk persistence.

The converter is intentionally separate from notification delivery.
This keeps cart snapshot persistence reusable if a future quote flow needs to create a quote without sending the same tenant notification.

The notification dispatcher resolves the tenant contact recipient before sending.
When no tenant contact email exists, it skips delivery and returns `None` instead of failing the quote conversion.

The owner-admin quote URL prefers an absolute `BASE_URL` when configured.
If no project base URL is available, the builder falls back to the tenant public website URL when present, and finally to a relative owner-admin path.

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
- SKU snapshots use the catalog variant effective SKU, so a variant without its own SKU snapshots the parent product base SKU
- attribute snapshots render in owner admin through the shared `core.forms.JsonKeyValueField` and Unfold's readonly widget delegation, so captured attributes keep the same key-value layout inside `readonly_fields` without becoming editable and empty snapshots show `-` placeholders

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

Current result DTOs:

- `CartQuoteRequestResultDTO`

Current result factories:

- `CartQuoteRequestResultDTOFactory`

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
- the change flow exposes terminal workflow buttons for completion and cancellation
- the changelist exposes bulk workflow actions for completion and cancellation
- destructive delete is disabled for quotes

Current owner-specific pieces:

- `QuoteModelAdmin`
- `QuoteItemModelInline`
- `QuoteItemModelInlineForm`
- `QuoteItemModelInlineFormSet`
- `QuotationAccessPolicy`
- `QuoteWorkflowTransitionService`

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
  - the owner can mark the quote as completed or cancelled from submit-line actions
- on changelist:
  - the owner can mark selected quotes as completed or cancelled through bulk actions
  - quotes that cannot transition are reported instead of being force-updated

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

The current owner admin exposes explicit terminal workflow actions while workflow timestamps remain read-only.

Current behavior:

- complete and cancel actions route through `QuoteWorkflowTransitionService`
- `requested_at` and `resolved_at` are read-only
- `requested_at` is derived the first time the workflow reaches `requested` or beyond
- `resolved_at` is derived the first time the workflow reaches `completed` or `cancelled`
- workflow transitions cannot move backward once the quote progresses
- terminal quotes no longer show complete or cancel submit-line actions

Future direction:

- keep the internal workflow focused on `draft`, `requested`, `in_progress`, `completed`, and `cancelled`
- keep any future `customer_status` as a second later dimension instead of overloading `workflow_status`
- only add customer-facing timestamps such as `sent_at` or `answered_at` once a real customer-facing quote flow exists
- attach future customer notifications or domain events to the workflow transition service rather than to owner-admin button code

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
- `quotation/tests/services/`

Project-level admin behavior tied to `quotation` currently lives in:

- `core/tests/adminsites/`

## What Should Live Here

Good candidates:

- quote lifecycle rules
- quote workflow transition services
- quote snapshot rules
- quote query helpers
- quote DTOs and DTO factories
- quote snapshot factories
- cart-to-quote conversion services
- quote notification request assembly and dispatching
- quotation-specific admin implementations

## What Should Not Live Here

Avoid placing unrelated project infrastructure in this app.

Examples:

- project admin site wiring
- global Unfold settings infrastructure
- catalog persistence rules
- storage configuration
