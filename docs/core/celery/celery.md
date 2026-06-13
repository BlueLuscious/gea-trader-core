# Celery

This document explains the project-wide Celery wiring under `core/celery.py`.

See also:

- `docs/project.md`
- `docs/core/core.md`
- `docs/core/celery/tasks/tasks.md`
- `docs/core/mail/mail.md`

## Goal

The Celery layer exists to provide one reusable asynchronous task runtime for the whole project.

It should:

- stay project-wide instead of mail-only
- use Redis as the shared local broker infrastructure
- keep the Celery bootstrap in `core/`
- allow future apps to add background tasks without reinventing the async stack

## Current Scope

The current implementation provides:

- one project Celery app in `core/celery.py`
- Django-settings-based Celery configuration
- Redis-backed broker and result backend settings
- code-based Celery Beat schedule wiring through `core/beat/`
- autodiscovery for installed app `tasks.py` modules
- autodiscovery for installed app `schedules` packages
- one first shared task implementation for outbound mail under `core/tasks/mail/tasks.py`

The first real async use case is outbound mail, but the stack remains intentionally general-purpose.

## Project Files

Current files:

- `core/celery.py`
- `core/beat/`
- `core/schedules/`
- `core/tasks/`

## Current Settings Direction

Celery reads its configuration from `core/settings.py` through the `CELERY_` namespace.

Current environment-driven settings:

- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `CELERY_TASK_ALWAYS_EAGER`

Current code-driven settings:

- `CELERY_BEAT_SCHEDULE`

Current default behavior:

- broker defaults to `REDIS_URL`
- result backend defaults to `REDIS_URL`
- tasks use JSON serialization
- broker retry on startup stays enabled
- eager mode is available for opt-in local or test scenarios

## Local Development

Redis is expected to be available locally through Docker:

- `127.0.0.1:6379`

Example local values:

- `REDIS_URL=redis://127.0.0.1:6379/0`
- `CELERY_BROKER_URL=redis://127.0.0.1:6379/0`
- `CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0`

Example worker command:

```powershell
.\.venv\Scripts\celery.exe -A core.celery worker --loglevel=info --pool=solo
```

On Windows local development, prefer `--pool=solo`.

This avoids the `billiard` multiprocessing permission errors that commonly appear with the default worker pool on Windows.

Example Beat command:

```powershell
.\.venv\Scripts\celery.exe -A core.celery beat --loglevel=info
```

Run Beat as a separate process from the worker.

Beat decides when a periodic task should be enqueued. A worker still has to be running to execute the task.

## Ownership Rule

Keep the Celery bootstrap in `core/`.

Keep the project-wide Beat schedule entrypoint in `core/beat/`.

Keep future domain task and schedule definitions close to the app that owns the business flow unless they are truly project-wide.

Examples:

- project-wide async infrastructure belongs in `core/`
- project-wide periodic schedules belong in `core/schedules/`
- app-owned business tasks should prefer living in the app that owns that workflow
- app-owned periodic schedules should prefer living in that app's `schedules/` package

For shared task placement and payload conventions, see:

- `docs/core/celery/tasks/tasks.md`

## Current Direction

The current direction on top of this wiring is:

1. keep the Celery runtime reusable for project-wide and app-owned background work
2. use thin tasks that delegate real work to services, composers, or app-level orchestration
3. keep outbound mail as the first real async use case, not as the only one
4. validate worker-backed flows through opt-in integration tests when one runtime crosses Redis, Celery, and external services

## Beat Schedule Direction

The current branch uses Celery Beat as the shared project scheduler for scheduled or periodic asynchronous work.

Current model:

- keep Beat as one generic scheduler for the whole project, not as one mail-specific runtime detail
- keep project-wide schedule definitions in `core/schedules/`
- keep app-owned schedule definitions in each owning app's `schedules/` package
- keep periodic task implementations in `core/tasks/` or the app-owned `tasks/` package that owns the workflow
- let Beat enqueue existing thin tasks instead of moving domain logic into the schedule layer

Current layout:

```text
core/
  celery.py
  beat/
    __init__.py
    celery_beat_schedule_builder.py
  schedules/
    __init__.py
```

Current direction:

- keep schedule definitions in code
- use the default Celery Beat scheduler first
- use Celery autodiscovery for installed app `schedules` packages
- let app-owned schedule modules define task-specific intervals in code
- avoid extra persistence or admin wiring until the project has a real periodic workload

Future evolution:

- move to `django-celery-beat` once the project needs database-backed periodic schedules
- use that evolution only when schedule changes must happen through the admin or without code deploys
- keep the current code-based model as the simpler default until that operational need becomes real

This remains intentionally separate from the current async mail feature.
