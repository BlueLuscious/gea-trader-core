# Core Mail Runtime

This document explains the current runtime behavior of the project-wide mail boundary.

See also:

- `docs/core/mail/mail.md`
- `docs/core/mail/templates.md`
- `docs/core/celery/celery.md`
- `docs/core/celery/tasks/tasks.md`

## Current Runtime Direction

The current mail implementation is intentionally:

- synchronous by default
- based on `django.core.mail`
- built on top of `EmailMultiAlternatives`
- able to build outbound messages either from raw DTO bodies or from Django templates
- already wired for asynchronous dispatch through the project-wide Celery runtime

This keeps the caller-facing boundary stable while allowing runtime delivery to grow.

## Shared Async Task Entrypoints

Mail async entrypoints live under the shared Celery task layer in:

- `core/tasks/mail/tasks.py`
- `send_mail_message_task`
- `send_templated_mail_task`

Current task logging direction:

- log task execution boundaries with compact operational context
- let the task and service layers log different boundaries instead of duplicating the same full event narrative

Current retry direction for both tasks:

- retry transient transport failures only
- current retryable errors:
  - `SMTPException`
  - `TimeoutError`
  - `ConnectionError`
- current retry policy:
  - `max_retries=3`
  - exponential backoff enabled
  - jitter enabled

## Current Settings Direction

The current project mail service uses the standard Django email settings from `core/settings.py`.

Current examples:

- `EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `DEFAULT_FROM_EMAIL`
- `BASE_URL` for absolute links when one mail flow needs them

Current meaning of `DEFAULT_FROM_EMAIL`:

- it is the project-level fallback sender used when one outbound message does not provide an explicit `from_email`
- it is appropriate for system-originated mail
- it is not the final tenant-owned sender identity for future business mail sent on behalf of one tenant
- future tenant-specific sender rules should stay separate from simple tenant contact metadata

## Sender And Reply Policy

The current project treats outbound mail identity in three separate layers:

1. technical sender
2. tenant contact channel
3. reply target

### Technical Sender

Current rule:

- `DEFAULT_FROM_EMAIL` is the system-level sender fallback
- it should be used for system-originated mail
- it should also be used for tenant-aware mail until a future tenant-specific verified sender flow exists

Current non-goal:

- do not treat `TenantModel.business_email` or `TenantModel.support_email` as the real authenticated SMTP sender
- do not set the customer's email address as `from_email`

Using an unverified tenant email or customer email as the real sender would blur technical sender identity and likely create deliverability problems.

### Tenant Contact Channel

Current rule:

- `support_email` is the preferred tenant contact channel
- `business_email` is the fallback tenant contact channel

These values represent business contact metadata, not the technical mail sender.

### Reply Target

Current rule:

- use `reply_to` to represent who should receive replies
- do not overload `from_email` to fake user or tenant identity

Recommended patterns:

- system mail:
  - `from_email = DEFAULT_FROM_EMAIL`
  - `reply_to = []` unless the system flow needs a specific reply target
- tenant notification mail sent to tenant staff:
  - `from_email = DEFAULT_FROM_EMAIL`
  - `to = tenant.support_email or tenant.business_email`
- customer-originated request forwarded to tenant staff:
  - `from_email = DEFAULT_FROM_EMAIL`
  - `reply_to = [customer_email]`
  - `to = tenant.support_email or tenant.business_email`
- future customer-facing tenant-aware mail:
  - `from_email = DEFAULT_FROM_EMAIL`
  - `reply_to = [tenant.support_email or tenant.business_email]` when a business reply channel should be exposed

This keeps the technical sender under project control while still allowing the correct human reply path.

For local development, the defaults target MailHog through SMTP.

Recommended local MailHog values:

- `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST=127.0.0.1`
- `EMAIL_PORT=1025`
- `EMAIL_HOST_USER=`
- `EMAIL_HOST_PASSWORD=`
- `EMAIL_USE_TLS=False`
- `EMAIL_USE_SSL=False`
- `DEFAULT_FROM_EMAIL=noreply@localhost`
- `BASE_URL=http://127.0.0.1:8000`

`BASE_URL` is documented as a shared project configuration in:

- `docs/core/config/config.md`

Within the mail runtime specifically, the current use of `BASE_URL` is:

- building absolute links included in outbound messages when the flow cannot rely on request-local host information

## Local Manual Smoke Test

One simple way to validate the runtime mail flow manually is:

1. start Docker services so MailHog is available
2. keep the local mail settings pointed at MailHog
3. send one message through `MailService`
4. confirm the message appears in the MailHog web UI

MailHog endpoints in local development:

- SMTP: `127.0.0.1:1025`
- Web UI: `http://127.0.0.1:8025`

## Tests

The mail package now follows the same split already used by storage:

- `core/tests/mail/unit/`
- `core/tests/mail/integration/`

### Unit Tests

Unit tests verify:

- DTO normalization
- `EmailMultiAlternatives` factory behavior
- synchronous delivery through Django's local memory backend
- template rendering
- template-based message DTO creation
- templated delivery through the local memory backend
- Celery-safe payload serialization and task delegation

### Integration Tests

Mail integration tests are opt-in and target MailHog through real SMTP delivery.

Enable them with:

- `RUN_MAIL_INTEGRATION_TESTS=True`
- `RUN_ASYNC_MAIL_INTEGRATION_TESTS=True` for the asynchronous worker-backed suite
- optional override: `MAILHOG_MESSAGES_API_URL=http://127.0.0.1:8025/api/v2/messages`
- optional override: `MAILHOG_WAIT_TIMEOUT_SECONDS=20`
- optional override: `MAILHOG_POLL_INTERVAL_SECONDS=0.25`

Current integration coverage verifies:

- sending one real message to MailHog
- sending multiple real messages to MailHog
- sending one real templated message to MailHog
- sending multiple real templated messages to MailHog
- sending one real tenant-aware templated message to MailHog
- sending multiple real tenant-aware templated messages to MailHog
- sending one real raw mail message through Celery to MailHog
- sending one real templated mail message through Celery to MailHog
- sending one real tenant-aware templated mail message through Celery to MailHog

The integration suite inspects MailHog through its HTTP API after the SMTP delivery succeeds.

The asynchronous integration subset additionally expects:

- Redis to be available
- one Celery worker to be running
- `CELERY_TASK_ALWAYS_EAGER=False`
- on Windows local development, the worker should use `--pool=solo`

Example command:

```powershell
$env:RUN_MAIL_INTEGRATION_TESTS='True'
.\.venv\Scripts\python.exe manage.py test core.tests.mail.integration
```

Asynchronous example command:

```powershell
$env:RUN_MAIL_INTEGRATION_TESTS='True'
$env:RUN_ASYNC_MAIL_INTEGRATION_TESTS='True'
.\.venv\Scripts\python.exe manage.py test core.tests.mail.integration.test_mailhog_async_mail_service_integration core.tests.mail.integration.test_mailhog_async_template_mail_service_integration
```

## Current Refinement Direction

The current structure is good enough for the base runtime, but the next refinement should keep mail policy responsibilities explicit.

Suggested responsibilities:

- `TenantMailContextResolver`
  - branding and contact context for templates
- `TenantMailRecipientResolver`
  - resolve the preferred tenant-facing `to` address
- `TenantMailReplyPolicy`
  - resolve the correct `reply_to` target for one business flow
- future `TenantMailSenderPolicy`
  - decide whether one flow should use the system sender fallback or a future verified tenant sender

The rule of thumb should be:

- resolvers gather data
- policies decide outbound mail behavior
- composers assemble already-decided payloads
- services send already-decided payloads

That split keeps the mail stack composable once customer-facing and async flows begin to grow.
