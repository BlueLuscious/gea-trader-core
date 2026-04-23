# Front Runtime Alignment Review

This document captures follow-up improvements for the current public storefront runtime.

It is meant to keep the ongoing front and quotation work aligned with `AGENTS.md`.

## Current Review Scope

The review focuses on:

- `front/` public storefront runtime
- reusable components used by the storefront shell
- `quotation/` cart-to-quote runtime integration
- cross-cutting mail and documentation touchpoints introduced by the current branch

## High-Priority Follow-Ups

### Encoding And Copy Consistency

Several files currently show mojibake-like Spanish strings in the working tree or terminal output.

Examples worth checking:

- `front/forms/quote_request_form.py`
- `front/components/cart-sidebar/cart-sidebar.html`
- `front/static/js/pages/product-detail.js`
- `quotation/templates/quotation/mail/messages/cart_quote_request_notification.html`
- `quotation/templates/quotation/mail/messages/cart_quote_request_notification.txt`
- `core/templates/mail/partials/footer.html`

Follow-up:

- verify the real on-disk encoding for these files
- normalize affected files to UTF-8 without corrupted characters
- preserve valid accented Spanish characters exactly as required by `AGENTS.md`

### Public Copy Versus Repository Language Rule

The repository currently mixes English structural code with Spanish literals in Python, templates, and JavaScript.

This is acceptable for real storefront copy, but it should be made more deliberate:

- keep public storefront copy consistent by surface
- keep code identifiers, comments, and documentation in English
- avoid mixing English and Spanish inside the same implementation concern unless the string is truly user-facing

### Translation Workflow Coverage

The current public storefront runtime adds stable user-facing strings but does not clearly distinguish:

- owner-admin strings that must follow the translation workflow immediately
- public storefront strings that may stay as direct source copy for now

Follow-up:

- document the current rule for public storefront copy in `docs/front/front.md`
- keep owner-admin and reusable admin-facing strings wrapped for translation
- avoid later moving admin copy through the codebase without matching `locale/es/LC_MESSAGES/django.po` updates

## Component-System Follow-Ups

### Reduce Inline Bootstrapping Scripts In Component Templates

Multiple components currently inject inline queue scripts directly from the component template.

Examples:

- `front/components/modal/modal.html`
- `front/components/cart-sidebar/cart-sidebar.html`

Follow-up:

- review whether the queue registration pattern can be centralized
- keep the current per-instance initialization contract
- reduce repetitive inline runtime code when a shared helper can preserve the same behavior

### Keep Base Components Strictly Agnostic

The current runtime is mostly aligned with the composition rules, but we should keep watching for domain drift in reusable pieces.

Examples to watch:

- `cart_sidebar` should stay a storefront shell and not absorb quote business rules
- `modal` and `toast` should remain generic runtime primitives
- any future quote-specific rendering should stay in templates or specialized views instead of entering base UI primitives

### Review The Sidebar Rendering Contract

The cart sidebar currently re-renders the full items region from server-rendered HTML fragments.

This is valid, but it creates a few trade-offs:

- animations become more sensitive to reflow timing
- client-side state restoration must be explicit
- the item and summary templates become part of the JSON API contract

Follow-up:

- document this pattern in `docs/front/front.md`
- decide whether future runtime fragments should remain server-rendered or move toward smaller JSON payloads plus client rendering
- keep one approach consistent per surface

## Runtime Flow Follow-Ups

### Cart Totals And Monetary Contract

The cart payload no longer exposes `subtotal` fields because they were unused.

That cleanup is good, but the next pricing step should be explicit:

- decide whether the cart should expose an estimated subtotal
- define whether quote-first products without public pricing participate in that total
- keep the summary template aligned with that pricing contract once it exists

### Quote Request Modal Lifecycle

The quote request form is now server-rendered in the base layout and submitted asynchronously.

Next refinements:

- decide whether the `GET /carrito/cotizar/` endpoint is still part of the intended contract
- remove it if the project no longer needs lazy server loading
- keep only one documented source of truth for initial modal rendering

### Better Empty And Converted Cart UX

The runtime currently closes the quote modal and restores its initial markup when the cart becomes empty.

Potential future refinements:

- disable quote actions more explicitly when the cart is empty
- add one clear converted-cart success state after quote submission
- decide whether a converted cart should remain inspectable for a short time or disappear immediately

## Tests And Verification Follow-Ups

### Keep Front Runtime Tests Close To The New Contract

The current branch already improved coverage, but the runtime work should keep growing with:

- modal pre-render coverage
- sidebar fragment rendering coverage
- cart quantity animation behavior at the integration level when practical
- quote request validation coverage for empty contact channels and empty carts

### Verify Required Project Commands For Important Front Changes

Per `AGENTS.md`, important component changes should validate:

- `manage.py check`
- `manage.py test front.tests`

When quotation runtime behavior changes materially, also consider:

- focused `quotation/tests/`
- focused `core/tests/mail/` coverage for tenant-aware notifications

## Documentation Follow-Ups

### Keep Front Docs In Sync With The Real Runtime

The branch has moved the public site beyond a simple shell.

Follow-up:

- update `docs/front/front.md` with the current cart runtime endpoints and modal strategy
- document the server-rendered fragment pattern used by the cart sidebar
- document the quote-request flow entrypoint from public storefront to `quotation/`

### Add Quotation Runtime Notes

`docs/quotation/quotation.md` currently describes the quote domain well, but it should also mention the new public cart-to-quote conversion service.

Recommended additions:

- service responsibility of `CartQuoteRequestService`
- relationship to `cart/`
- tenant notification side effects

## Ongoing Rule Reminder

When continuing this branch, prefer:

1. agnostic base components
2. server and client contracts that are small and explicit
3. docstrings and typing on every new Python class, function, and method
4. English repository structure with deliberate handling of Spanish user-facing copy
5. tests and docs updated in the same task when runtime behavior changes
