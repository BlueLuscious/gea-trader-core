# gea-trader-core

## Description

gea-trader-core is the product management system used by the GEA Trader
company. It is a Django application providing CRUD operations, business
logic and a translation workflow for managing products and related data.

## Requirements

- Python 3.11+ (run in a virtual environment)
- Docker (used to run the local PostgreSQL, MinIO, MailHog, and Redis services)
- gettext tools for message catalog management (see [Translations](#translations) below)

## Development setup

Follow these steps to get a development copy running locally:

1. **Clone the repository**

   ```bash
   git clone https://github.com/BlueLuscious/gea-trader-core.git
   cd gea-trader-core
   ```
2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # Unix/macOS
   source .venv/bin/activate
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Run Docker**

   Local infrastructure is provided by Docker. The Django application
   runs on your host but connects to containerized services.

   By default, `docker compose up -d` starts:

   - PostgreSQL for the development database
   - MinIO for local S3-compatible storage testing
   - MinIO Client bootstrap logic to create the configured bucket automatically
   - MailHog for local SMTP capture and mail preview
   - Redis as the shared local broker for future asynchronous project tasks

   Bring up the local services before running migrations or the
   development server.

   ```bash
   docker compose up -d
   ```

   MailHog is available locally at:

   - SMTP: `127.0.0.1:1025`
   - Web UI: `http://127.0.0.1:8025`

   Redis is available locally at:

   - Redis: `127.0.0.1:6379`
5. **Apply migrations**

   ```bash
   python manage.py migrate
   ```
6. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   Done!

## Configuration Notes

- Documentation map lives at:
  - `docs/project.md`
- The main environment example is:
  - `.env.example`
- Storage configuration documentation lives at:
  - `docs/core/config/storage/storage.md`
- Storage testing documentation lives at:
  - `docs/core/config/storage/testing.md`
- Logging configuration documentation lives at:
  - `docs/core/config/logging/logging.md`
- Celery runtime documentation lives at:
  - `docs/core/celery/celery.md`
- Mail service documentation lives at:
  - `docs/core/mail/mail.md`
- Mail runtime documentation lives at:
  - `docs/core/mail/runtime.md`
- Mail template documentation lives at:
  - `docs/core/mail/templates.md`
- Admin site infrastructure documentation lives at:
  - `docs/core/adminsites/adminsites.md`
- Future owner-managed app wiring documentation lives at:
  - `docs/core/adminsites/owner-managed-apps.md`
- Accounts app documentation lives at:
  - `docs/accounts/accounts.md`
- Tenancy app documentation lives at:
  - `docs/tenancy/tenancy.md`
- Tenancy runtime documentation lives at:
  - `docs/tenancy/runtime.md`
- Tenancy access-policy documentation lives at:
  - `docs/tenancy/access.md`
- Catalog app documentation lives at:
  - `docs/catalog/catalog.md`
- Quotation app documentation lives at:
  - `docs/quotation/quotation.md`
- Ready-to-copy environment examples live under:
  - `docs/env-examples/`

If you are using local S3-compatible storage during development, make sure your `.env` is aligned with the MinIO credentials and bucket configured in `docker-compose.yml`.

If you want the default mail service to deliver into MailHog locally, keep these values aligned with your `.env`:

- `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST=127.0.0.1`
- `EMAIL_PORT=1025`
- `DEFAULT_FROM_EMAIL=noreply@localhost`

If you want local async infrastructure ready for Celery or future background tasks, keep this value aligned with your `.env`:

- `REDIS_URL=redis://127.0.0.1:6379/0`

If you want to run a local Celery worker after Redis is available, use:

```bash
# Windows
.venv\Scripts\celery.exe -A core.celery worker --loglevel=info --pool=solo

# Unix/macOS
.venv/bin/celery -A core.celery worker --loglevel=info
```

On Windows local development, prefer `--pool=solo` to avoid the `billiard` multiprocessing permission errors that commonly appear with the default worker pool.

If you want to run local periodic tasks after Redis is available, run Celery Beat in a separate terminal:

```bash
# Windows
.venv\Scripts\celery.exe -A core.celery beat --loglevel=info

# Unix/macOS
.venv/bin/celery -A core.celery beat --loglevel=info
```

Beat only enqueues scheduled tasks. Keep one Celery worker running separately to execute them.

## Translations

The project uses Django's internationalization framework. To work with
translations you will need the GNU gettext utilities. On Windows you can
download a build from the following link:

- [Gettext for Windows](https://github.com/mlocati/gettext-iconv-windows/releases/tag/v1.0-v1.18-r3)

To extract new strings and create or update message files:

```bash
python manage.py makemessages -l <lang> --ignore .venv --ignore node_modules --ignore '*.txt'
```

After editing the `.po` files, compile them so Django can use them:

```bash
python manage.py compilemessages -l <lang>
```
