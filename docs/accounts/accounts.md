# Accounts App

This document explains the purpose and structure of the `accounts/` app.

## Goal

`accounts/` provides the authentication domain for the project.

It currently defines the custom Django user model and the first admin registrations required to manage authentication data inside the project admin sites.

## Current Structure

Current contents:

- `apps.py`
- `models/`
- `admin/`
- `migrations/`
- `tests/`

## Responsibilities

The `accounts/` app is responsible for:

- defining the project's user model
- exposing user query infrastructure
- registering authentication-related admins where needed

It should remain focused on authentication and account-level concerns.

## Models

### `UserModel`

`UserModel` extends Django's `AbstractUser` and acts as the project's `AUTH_USER_MODEL`.

Current behavior:

- preserves Django auth compatibility
- exposes a typed custom manager

Related files:

- `accounts/models/user_model.py`
- `accounts/models/managers/user_model_manager.py`
- `accounts/models/querysets/user_model_queryset.py`

## Manager and QuerySet

The app follows the project model structure convention:

- model
- queryset
- manager

Current pieces:

- `UserModelQuerySet`
- `UserModelManager`

At the moment the queryset layer is intentionally small, but the structure is already in place for reusable account filters and query helpers.

## Admin

The app already integrates with the custom project admin site structure.

Current registrations live in:

- `accounts/admin/master/`
- `accounts/admin/owner/`

Current master registrations:

- `UserModelAdmin`
- `GroupAdmin`

These admins are registered against the shared `master_admin_site`.

Current owner registrations:

- `OwnerUserModelAdmin`

The owner admin currently exposes a curated `Accounts > Users` flow.

Current owner behavior:

- users are managed as support or operator accounts
- superusers are hidden from the owner queryset
- hard delete is disabled in favor of deactivation
- owners cannot remove their own owner-admin access accidentally from the edit screen
- direct group management is intentionally postponed until group ownership and visibility rules are defined

This keeps the authentication admin visible inside the master admin site while following the project rule of keeping domain admin logic inside each app.

## Relationship With `core/adminsites/`

`accounts/` should own its admin implementations.

`core/adminsites/` should only provide:

- admin site classes
- shared site instances
- site-level infrastructure

This separation keeps domain admin behavior near the app that owns the models.

## What Should Live Here

Good candidates:

- custom authentication model behavior
- account-specific query helpers
- account-specific admin implementations
- future account DTOs or services if the domain grows

## What Should Not Live Here

Avoid placing unrelated platform infrastructure in this app.

Examples:

- project-wide admin site wiring
- global settings resolution
- storage infrastructure

Those concerns belong in `core/`.
