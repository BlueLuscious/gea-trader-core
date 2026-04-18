# Core Mail

This document explains the project-wide outbound mail boundary under `core/mail/`.

See also:

- `docs/project.md`
- `docs/core/core.md`
- `docs/core/mail/runtime.md`
- `docs/core/mail/templates.md`
- `docs/core/mail/composers.md`

## Goal

`core/mail/` exists to provide one reusable outbound mail boundary for the whole project.

It should:

- keep mail delivery out of domain apps
- expose one stable service contract
- build on top of Django's native mail stack
- stay reusable across synchronous and asynchronous delivery flows

## Current Structure

Current contents:

- `dtos/`
- `backends/`
- `composers/`
- `factories/`
- `renderers/`
- `resolvers/`
- `serializers/`
- `policies/`
- `services/`

## Responsibilities

### `MailService`

`MailService` is the raw outbound mail entrypoint.

Current responsibilities:

- send one mail message
- send multiple mail messages
- enqueue one raw mail message for asynchronous delivery
- delegate actual delivery to the configured project backend
- log meaningful delivery and enqueue boundaries without logging full message bodies

### `TemplateMailComposer`

`TemplateMailComposer` is the composition entrypoint for templated outbound mail.

Current responsibilities:

- accept one `TemplateMailRequestDTO`
- resolve sender policy
- bind one explicit tenant context when needed
- render one plain-text and one HTML template
- build one `MailMessageDTO`

It does not send mail.

For composer usage and design rules, see:

- `docs/core/mail/composers.md`

### `TemplateMailService`

`TemplateMailService` is the higher-level entrypoint for templated outbound mail.

Current responsibilities:

- accept one `TemplateMailRequestDTO`
- delegate mail composition to `TemplateMailComposer`
- enqueue one templated mail request for asynchronous delivery
- delegate final delivery to `MailService`
- log meaningful templated delivery and enqueue boundaries without duplicating low-level renderer details

### DTOs

The DTO layer exists so the service contract stays explicit and easy to evolve.

Current DTOs:

- `MailRecipientDTO`
- `MailAttachmentDTO`
- `MailMessageDTO`
- `TemplateMailRequestDTO`

This keeps mail payload assembly separate from Django's concrete message object.

### `backends/`

This package owns delivery implementations.

Current backend:

- `DjangoMailDeliveryBackend`

It sends mail through Django's configured email backend.

### `factories/`

This package owns translation from project DTOs into framework objects.

Current factories:

- `EmailMultiAlternativesFactory`
- `TemplateMailMessageFactory`

They convert:

- one `MailMessageDTO` into one Django `EmailMultiAlternatives` instance
- one `TemplateMailRequestDTO` into one `MailMessageDTO`

### `serializers/`

This package owns conversion between mail DTOs and Celery-safe payload dictionaries.

Current serializers:

- `MailMessagePayloadSerializer`
- `TemplateMailRequestPayloadSerializer`

They convert:

- one `MailMessageDTO` into one plain async payload and back
- one `TemplateMailRequestDTO` into one plain async payload and back

### `renderers/`

This package owns mail template rendering.

Current renderer:

- `MailTemplateRenderer`

It renders the HTML and plain-text mail templates after merging the tenant-aware base context.

### `resolvers/`

This package owns mail data lookups and assembly helpers.

Current resolvers:

- `MailTemplateBaseContextBuilder`
- `TenantMailContextResolver`
- `TenantMailRecipientResolver`

They gather:

- the effective base template context shared by synchronous rendering and asynchronous templated snapshotting
- tenant-aware template context values
- preferred tenant contact recipients

### `policies/`

This package owns outbound mail behavior decisions.

Current policies:

- `SystemMailSenderPolicy`
- `TenantMailReplyPolicy`

They decide:

- which technical sender override should be used when one exists
- which reply target fits one business flow

## Related Docs

Use these documents together:

- `docs/core/mail/runtime.md`
  - runtime behavior, async tasks, settings, sender and reply policy, smoke tests, and test coverage
- `docs/core/mail/templates.md`
  - template layout structure, tenant-aware template context, and template extension rules
- `docs/core/mail/composers.md`
  - composer-specific usage and design guidance

## What Should Live Here

Good candidates:

- project-wide mail DTOs
- project-wide mail delivery services
- framework-specific mail factories
- async task entrypoints for outbound mail

## What Should Not Live Here

Avoid placing these here:

- domain-specific email business rules
- email template content that belongs to one app only
- domain orchestration for account flows, tenancy flows, or future domain apps

Those concerns should stay in the app that decides when a mail should be sent.
