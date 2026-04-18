# Celery Task Conventions

This document explains the shared conventions for asynchronous tasks built on top of the project-wide Celery runtime.

See also:

- `docs/core/celery/celery.md`
- `docs/project.md`

## Goal

The project should use Celery as one reusable asynchronous execution layer, not as one mail-only detail.

Task conventions should make it easy to:

- add async work without reinventing the same patterns
- keep project-wide concerns in `core/`
- keep domain behavior close to the app that owns it
- avoid request-bound or non-serializable task payloads

## Ownership Rule

Use this split:

- `core/` owns the async runtime and project-wide tasks
- domain apps own their business tasks

Recommended placement:

- `core/tasks/`
  - only for truly project-wide tasks
- `<app>/tasks/`
  - preferred for app-owned business flows
- `<app>/tasks.py`
  - acceptable only for very small apps with one tiny task surface

Examples:

- project-wide mail infrastructure can live in `core/tasks/`
- a quotation-specific follow-up task should prefer living in `quotation/tasks/`

## Payload Rule

Tasks should accept only serialized, explicit payloads.

Prefer:

- ids
- strings
- numbers
- booleans
- plain dictionaries
- plain lists and tuples of serialized values

Avoid passing:

- `request`
- ORM model instances
- lazy querysets
- complex Python objects that depend on in-memory state

## Logic Rule

Keep Celery tasks thin.

The task should usually:

1. accept a serialized payload
2. delegate quickly to a service, composer, or orchestrator
3. return one simple result or nothing

Do not turn the task into the place that owns the business workflow.

## Naming Rule

Use explicit names ending in `_task`.

Examples:

- `send_mail_message_task`
- `send_templated_mail_task`
- `send_quotation_inquiry_email_task`

Avoid vague names such as:

- `process_email`
- `handle_notification`
- `run_job`

Prefer `tasks.py` as the module name inside one task package or subpackage.

Preferred examples:

- `core/tasks/mail/tasks.py`
- `quotation/tasks/email/tasks.py`
- `quotation/tasks/reminders/tasks.py`

Avoid file names such as:

- `mail_tasks.py`
- `email_tasks.py`
- `reminder_tasks.py`

## Current Recommended Structure

Current recommended layout:

```text
core/
  tasks/
    __init__.py
    mail/
      __init__.py
      tasks.py

quotation/
  tasks/
    __init__.py
    email/
      __init__.py
      tasks.py
```

This reflects the current direction:

- project-wide async infrastructure in `core/`
- app-owned business flows inside the app that owns them
- `tasks.py` as the default Celery module name inside each task package

## Service Boundary Rule

Keep this split:

- Celery executes
- services or composers decide

Examples:

- one mail task should delegate to the existing mail service or composer layers
- one quotation task should delegate to one quotation service or one quotation-specific mail composer

## Retry Rule

Start with task-local retry decisions.

Prefer:

- explicit `autoretry_for`
- explicit `retry_backoff`
- explicit `retry_kwargs`

Only extract one shared task base class once real repetition appears across multiple tasks.

Current mail-task direction:

- retry only transient transport or connection failures
- do not retry payload, template, or business-logic errors
- keep retries explicit on each task until more shared repetition appears

## Testing Rule

Prefer this order:

1. unit test the service or composer that owns the real work
2. unit test the task wrapper to verify dispatch and payload handoff
3. add integration coverage only when the async flow becomes important enough to justify worker-level testing

## Rule Of Thumb

When deciding where one async behavior should live:

- if it is infrastructure-wide, keep it in `core/`
- if it belongs clearly to one app, keep it in that app
- if the task needs complex business decisions, move those decisions into services or composers instead of growing the task body
