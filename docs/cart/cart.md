# Cart App

This document explains the purpose and structure of the `cart/` app.

## Goal

`cart/` provides the persisted runtime basket used by the project before one cart may originate a quotation flow.

It currently defines:

- persisted carts and cart items
- typed query infrastructure for cart runtime data
- tenant-aware ownership at the cart root
- DTOs and DTO factories for higher layers
- master admin registrations for technical visibility
- translation-ready runtime and model copy

The app should remain focused on runtime basket state rather than owner-managed CRUD behavior.

## Current Structure

Current contents:

- `apps.py`
- `choices/`
- `models/`
- `services/`
- `schedules/`
- `tasks/`
- `dtos/`
- `admin/`
- `migrations/`
- `tests/`

## Responsibilities

The `cart/` app is responsible for:

- defining persisted cart lifecycle data
- storing concrete cart items linked to catalog products and optional variants
- scoping carts to the owning business
- exposing reusable cart query helpers
- supporting runtime-origin quotation flows
- keeping technical cart visibility available in the master admin

## Runtime Role

`cart/` is a runtime-only domain.

Current direction:

- `cart/` stays outside the owner admin and owner sidebar
- `cart/` is not treated as an owner-managed CRUD surface
- future owner-facing visibility should likely appear as dashboard metrics, summaries, or support views rather than editable rows

The current public cart HTTP endpoints live in `front/`.
They use the `cart/` models, managers, and querysets as persistence infrastructure, but the request parsing, JSON response contract, and server-rendered sidebar fragments remain storefront concerns.

This keeps carts aligned with live transactional state rather than curated business configuration.

## Models

### `CartModel`

`CartModel` represents the persisted basket root.

Current fields cover:

- mandatory business ownership through `tenant`
- optional customer linkage through `user`
- optional anonymous runtime linkage through `session_key`
- lifecycle status
- optional expiration timestamp
- audit timestamps

Related files:

- `cart/models/cart_model.py`
- `cart/models/querysets/cart_model_queryset.py`
- `cart/models/managers/cart_model_manager.py`

### `CartItemModel`

`CartItemModel` stores one concrete line inside a cart.

Current fields cover:

- parent cart
- selected product
- optional selected variant
- quantity
- optional notes
- audit timestamps

Current validation rules:

- the selected product must belong to the same tenant as the parent cart
- the selected variant must belong to the selected product

Current intent:

- cart items stay tenant-scoped through their parent `CartModel`
- cart items reflect current catalog references rather than quote-style snapshots

Related files:

- `cart/models/cart_item_model.py`
- `cart/models/querysets/cart_item_model_queryset.py`
- `cart/models/managers/cart_item_model_manager.py`

## Choices

The app keeps cart lifecycle choices outside the model.

Current choice enum:

- `CartStatus`

This keeps runtime status values reusable across models, admins, DTOs, and future services.

The choice labels are also translation-ready.

## Query And DTO Direction

The app already includes typed query helpers, DTOs, and DTO factories.

Current queryset helpers include:

- `CartModelQuerySet.for_tenant(...)`
- `CartModelQuerySet.active()`
- `CartModelQuerySet.converted()`
- `CartModelQuerySet.abandoned()`
- `CartModelQuerySet.expired(...)`
- `CartModelQuerySet.for_session(...)`
- `CartModelQuerySet.for_user(...)`
- `CartItemModelQuerySet.for_tenant(...)`
- `CartItemModelQuerySet.for_cart(...)`
- `CartItemModelQuerySet.with_catalog()`

Current DTOs:

- `CartModelDTO`
- `CartItemModelDTO`

Current factories:

- `CartModelDTOFactory`
- `CartItemModelDTOFactory`

Current DTO direction:

- `CartModelDTO` includes `tenant_id` so higher layers can keep cart ownership explicit
- `CartItemModelDTO` stays scoped through `cart_id` instead of duplicating `tenant_id`

## Admin

The app integrates only with the master admin site:

- `cart/admin/master/`

### Master Admin

The master admin keeps carts and cart items visible as raw technical runtime entities.

Current registrations:

- `CartModelAdmin`
- `CartItemModelAdmin`

Current direction:

- master admin keeps technical visibility and search support
- tenant context is visible for debugging and support
- this does not imply that `cart/` should become owner-managed

### Owner Admin

`cart/` is intentionally not registered in the owner admin.

Current direction:

- no owner sidebar link
- no owner CRUD surface
- no cart-specific owner access policy

If owner-facing cart visibility appears later, it should likely be expressed through metrics or support-oriented views rather than direct row editing.

## Relationship To Quotation

`quotation/` may optionally reference `CartModel` as its source basket.

Current direction:

- carts are tenant-owned at the cart root
- quotes are tenant-owned at the quote root
- one quote cannot reference a cart from another tenant

This keeps cart-origin quotation flows tenant-safe without turning `cart/` into an owner-managed app.

See also:

- `docs/quotation/quotation.md`

## Logging

`cart/` applies logging only at meaningful runtime boundaries.

Current logged boundaries:

- expired-cart closure task execution

Future likely logging boundaries:

- cart creation or update flows
- conversion from cart to quote
- future owner dashboard metrics derived from cart runtime data

## Expiration Processing

`cart/` owns the business behavior for closing expired carts.

Current behavior:

- `CartExpirationService.close_expired_carts()` marks active carts whose `expires_at` timestamp has passed as `abandoned`
- converted carts are not touched by expiration processing
- carts without an expiration timestamp are not touched
- `close_expired_carts_task` delegates to the service and logs the number of carts closed
- `cart/schedules/` owns the Celery Beat schedule that enqueues `close_expired_carts_task`
- public runtime carts currently receive an expiration timestamp twenty-four hours after creation

The schedule interval is code-owned and currently runs every thirty minutes instead of introducing one environment variable per periodic task.
`core` only discovers installed app schedule packages and provides the shared Beat runtime.

See also:

- `docs/core/celery/celery.md`

## Translation

The cart runtime and model copy is now prepared for the project translation workflow.

Current translation-ready pieces:

- `CartConfig.verbose_name`
- cart status choice labels
- cart model labels and help texts
- cart item model labels and help texts
- cart runtime validation errors

## Tests

The app already follows the project test structure convention.

Current test areas:

- `cart/tests/models/`
- `cart/tests/managers/`
- `cart/tests/querysets/`
- `cart/tests/services/`
- `cart/tests/schedules/`
- `cart/tests/tasks/`
- `cart/tests/dtos/`
- `cart/tests/factories/`

Project-level admin behavior tied to the runtime role of `cart` currently lives in:

- `core/tests/adminsites/`

## What Should Live Here

Good candidates:

- cart lifecycle rules
- cart-item runtime consistency rules
- cart query helpers
- cart DTOs and DTO factories
- runtime orchestration for future cart flows

## What Should Not Live Here

Avoid placing unrelated project infrastructure or owner CRUD behavior in this app.

Examples:

- owner-admin registrations for direct cart editing
- global admin site wiring
- quotation snapshot rules
- catalog persistence rules
- storage configuration
