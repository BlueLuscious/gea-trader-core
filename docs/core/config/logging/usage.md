# Logging Usage Rules

This document explains how project code should use the shared logging base.

See also:

- `docs/project.md`
- `docs/core/config/logging/logging.md`
- `docs/core/celery/celery.md`
- `docs/core/mail/mail.md`

## Goal

The shared logging base exists to support operational visibility without turning logs into noise.

Project code should use logs to:

- explain meaningful runtime events
- surface failures and unexpected states
- support debugging and operations

Project code should not use logs to:

- replace validation
- replace tests
- narrate trivial control flow
- dump sensitive data

## Logger Rule

Modules should define their logger like this:

```python
import logging

logger = logging.getLogger(__name__)
```

This keeps logger names aligned with package ownership automatically.

## Level Rule

### `DEBUG`

Use `debug` for low-level technical detail that is mainly helpful during development or targeted troubleshooting.

Examples:

- resolved payload shapes
- selected configuration branches
- optional runtime details that would be too noisy at `INFO`

Avoid `debug` for:

- expected high-volume loops
- values that may expose sensitive data

### `INFO`

Use `info` for meaningful expected runtime events.

Examples:

- one async task was enqueued
- one outbound mail flow completed successfully
- one storage adapter was selected from configuration
- one tenant switch or similar operational boundary completed successfully

Use `info` when an operator or developer may reasonably want to understand that the event happened during normal execution.

### `WARNING`

Use `warning` for unexpected but recoverable situations.

Examples:

- one optional dependency is unavailable and the code falls back safely
- one expected external resource could not be resolved and the flow continues with a safe fallback
- one suspicious runtime state appears but does not break the request or task

Do not use `warning` for fully expected outcomes that are already part of normal business behavior.

### `ERROR`

Use `error` when one operation failed and the current code path cannot complete as intended.

Examples:

- one mail delivery attempt failed
- one external service call failed without an immediate recovery path
- one storage operation failed and the user-visible action cannot succeed

Use `error` when you want a clear operational signal but you are handling the failure explicitly.

### `EXCEPTION`

Use `exception` inside an `except` block when the traceback matters.

Examples:

- one integration boundary failed and the traceback is useful for diagnosis
- one Celery task catches and re-raises or translates a failure

Prefer `logger.exception(...)` over logging a traceback manually.

## Where To Log

Prefer logging at operational boundaries.

Good candidates:

- service entrypoints and outcomes
- Celery task enqueue and execution boundaries
- external integrations such as mail or storage
- tenant resolution or tenant switching boundaries
- meaningful admin or view actions that change state

## Where Not To Log

Avoid logging in low-value or high-noise places.

Examples:

- DTOs
- simple factories
- value normalizers
- trivial manager or queryset wrappers
- deeply repeated helper methods unless they represent a real failure boundary

## Duplication Rule

Log one event at the boundary that owns it.

Examples:

- if one service handles an external API failure, prefer logging there instead of in every lower helper
- if one Celery task delegates to one service, avoid logging the same success event in both places unless the two logs serve different operational purposes

The goal is:

- enough visibility to diagnose problems
- not multiple nearly identical log lines for the same event

## Sensitive Data Rule

Never log:

- passwords
- secrets
- access tokens
- full credentials
- raw private keys
- full email bodies when not operationally necessary
- personal data unless there is a clear operational reason and the exposure is acceptable

When useful, log stable identifiers or short summaries instead.

Examples:

- tenant id
- user id
- task id
- mail subject summary
- provider name

## Services Rule

Services should log:

- meaningful entry or exit events when they represent operational boundaries
- failures at integration points
- important fallback behavior

Services should not log every internal step unless troubleshooting value clearly justifies it.

## Celery Task Rule

Tasks should stay thin and log only what belongs to the task boundary.

Good examples:

- task received one payload
- task completed one external side effect
- task failed because one external integration failed

Avoid turning task logs into full business narration when the owning service already explains the meaningful event.

## Test Rule

Tests should not be rewritten just to satisfy logging.

When adding logging to runtime code:

- keep tests focused on behavior
- add log assertions only when the log output is part of an important operational contract

## Rollout Rule

Apply logging incrementally and intentionally.

Start with:

- `core/mail/`
- `core/tasks/`
- `core/config/storage/`
- `core/adminsites/`
- `core/i18n/`
- `tenancy/`
- `accounts/`

Only expand into future domain apps when the active branch needs it.
