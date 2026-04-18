# Logging Configuration

This document explains the shared logging configuration layer under `core/config/logging/`.

See also:

- `docs/project.md`
- `docs/core/core.md`
- `docs/core/config/config.md`
- `docs/core/config/logging/usage.md`
- `docs/core/celery/celery.md`

## Goal

The logging layer exists to provide one reusable project-wide logging base for:

- Django runtime code
- app-owned runtime code
- Celery workers and shared async tasks

The base configuration should stay:

- environment-driven
- readable
- flexible
- easy to extend later without rewriting `core/settings.py`

## Current Scope

The current implementation provides:

- one logging builder in `core/config/logging/logging_config_builder.py`
- one shared console handler
- one readable text formatter
- environment-driven log levels
- logger namespaces derived from the explicit `PROJECT_APPS` runtime list

The first phase intentionally keeps logging simple:

- console output only
- no file handler yet
- no JSON formatter yet
- no external logging provider yet

## Project Files

Current files:

- `core/config/logging/`
- `core/settings.py`

## Current Environment Variables

The shared logging configuration currently reads:

- `LOG_LEVEL`
- `DJANGO_LOG_LEVEL`
- `CELERY_LOG_LEVEL`

Current default direction:

- `LOG_LEVEL`
  - `DEBUG` when `DEBUG=True`
  - `INFO` when `DEBUG=False`
- `DJANGO_LOG_LEVEL`
  - `INFO` when `DEBUG=True`
  - `WARNING` when `DEBUG=False`
- `CELERY_LOG_LEVEL`
  - `INFO` by default

These values can be overridden explicitly per environment.

## Current Formatter Direction

The default formatter is a readable text line with:

- timestamp
- level
- logger name
- message

Current format:

```text
%(asctime)s | %(levelname)s | %(name)s | %(message)s
```

## Logger Namespace Direction

Modules should use:

```python
import logging

logger = logging.getLogger(__name__)
```

This keeps logger names aligned automatically with package ownership.

Current project namespaces are derived from the explicit `PROJECT_APPS` list in `core/settings.py`.

With the current branch scope, that means:

- `core`
- `accounts`
- `tenancy`
- `django`
- `celery`

## Relationship With `settings.py`

`core/settings.py` should consume the logging configuration through the builder rather than defining one large inline dictionary.

The current pattern is:

- `core/settings.py` resolves `DEBUG`
- `core/settings.py` defines `PROJECT_APPS`
- `LoggingConfigBuilder` builds the final `LOGGING` value

This keeps the settings file readable and makes the logging configuration easier to test.

## Deferred Improvements

The current base does not yet include:

- file handlers
- structured JSON logging
- request correlation ids
- external log aggregation
- more specialized logger tuning per package

Those can be added later once the project has real operational pressure for them.
