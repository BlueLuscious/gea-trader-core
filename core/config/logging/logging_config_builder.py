""" Build the project-wide Django logging configuration. """

import os
from typing import Any


class LoggingConfigBuilder:
    """ Build one reusable logging configuration for the whole project. """

    @classmethod
    def build(cls, *, debug: bool, project_apps: list[str]) -> dict[str, Any]:
        """ Build the Django `LOGGING` setting for the current environment.

        Args:
            debug: Whether Django is running in debug mode.
            project_apps: Project-owned Django apps active in the current runtime.

        Returns:
            dict[str, Any]: Logging configuration compatible with Django settings.
        """
        app_log_level = cls._resolve_log_level(
            env_name="LOG_LEVEL",
            default="DEBUG" if debug else "INFO",
        )
        django_log_level = cls._resolve_log_level(
            env_name="DJANGO_LOG_LEVEL",
            default="INFO" if debug else "WARNING",
        )
        celery_log_level = cls._resolve_log_level(
            env_name="CELERY_LOG_LEVEL",
            default="INFO",
        )
        project_logger_namespaces = cls._resolve_project_logger_namespaces(project_apps)

        project_loggers = {
            namespace: {
                "handlers": ["console"],
                "level": app_log_level,
                "propagate": False,
            }
            for namespace in project_logger_namespaces
        }

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": app_log_level,
                },
            },
            "root": {
                "handlers": ["console"],
                "level": app_log_level,
            },
            "loggers": {
                **project_loggers,
                "django": {
                    "handlers": ["console"],
                    "level": django_log_level,
                    "propagate": False,
                },
                "celery": {
                    "handlers": ["console"],
                    "level": celery_log_level,
                    "propagate": False,
                },
            },
        }

    @staticmethod
    def _resolve_log_level(*, env_name: str, default: str) -> str:
        """ Resolve one environment-driven logging level.

        Args:
            env_name: Environment variable name to inspect.
            default: Fallback log level when the environment variable is missing.

        Returns:
            str: Uppercase logging level string.
        """
        return os.environ.get(env_name, default).strip().upper() or default

    @staticmethod
    def _resolve_project_logger_namespaces(project_apps: list[str]) -> tuple[str, ...]:
        """ Resolve the project logger namespaces from the current installed apps.

        Args:
            project_apps: Project-owned Django apps active in the current runtime.

        Returns:
            tuple[str, ...]: Ordered logger namespaces for current project apps.
        """
        return tuple(dict.fromkeys(project_apps))
