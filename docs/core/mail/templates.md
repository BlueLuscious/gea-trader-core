# Core Mail Templates

This document explains the shared mail template structure under `core/templates/core/mail/`.

See also:

- `docs/core/mail/mail.md`
- `docs/core/mail/runtime.md`
- `docs/core/mail/composers.md`

## Goal

The shared mail templates exist to provide one reusable layout and context contract for project-wide outbound mail.

They should:

- render both HTML and plain text together
- keep system-wide layout and footer structure reusable
- support tenant-aware branding and contact context when one tenant is active
- degrade to neutral content when no tenant-aware context exists

## Current Template Structure

Mail templates live under:

- `core/templates/core/mail/layouts/`
- `core/templates/core/mail/partials/`
- `core/templates/core/mail/messages/`

Current structure:

- one reusable HTML base layout
- one reusable plain-text base layout
- one mandatory footer partial in both formats
- one reusable CTA button partial for HTML mails
- one generic example message template pair

## Current Layout Direction

The current layout direction is:

- always render plain text and HTML together
- keep the system footer structure mandatory
- resolve tenant-aware branding and contact values from the active tenant context when one exists
- keep branding values optional when no active tenant context exists
- allow future template override by template name
- avoid full layout replacement as the default extension path

## Current Tenant-Aware Template Behavior

Current tenant-aware behavior:

- `product_name` resolves from tenant branding display data first, then the tenant business name
- `support_email` resolves from tenant operational contact data on `TenantModel`, with business email as a fallback
- `phone_number` and `website_url` resolve from tenant operational contact data on `TenantModel`
- `TemplateMailService` may use either the active runtime tenant context or one explicit tenant passed by the caller
- when neither value exists, templates should degrade to a neutral layout instead of inventing unrelated branding

## Current Context Assembly Direction

The shared template context is assembled so synchronous and asynchronous templated mail use the same base context direction.

Current pieces:

- `MailTemplateBaseContextBuilder`
- `TenantMailContextResolver`
- `MailTemplateRenderer`
- `TemplateMailRequestPayloadSerializer`

Current rule:

- build the effective base context once
- let explicit caller context override shared defaults
- snapshot the effective templated context during async enqueue instead of reloading tenant state inside the worker

## Extension Rule

When adding one new shared mail template:

1. keep the shared layout contract intact
2. prefer adding a new message template pair under `messages/`
3. keep footer and shared CTA structure reusable through partials
4. add new context keys through resolvers or builders instead of hardcoding unrelated defaults in the template
5. keep tenant-aware context optional unless the business flow truly requires it

## What Should Live Here

Good candidates:

- shared mail layouts
- reusable mail partials
- template contracts reused across multiple project mail flows
- tenant-aware template context guidance

## What Should Not Live Here

Avoid placing these here:

- domain-specific business email copy tied to one app only
- sender and reply policy rules
- Celery task behavior
- transport-layer mail settings

Those concerns belong in:

- `docs/core/mail/runtime.md`
- or the app that owns the business flow
