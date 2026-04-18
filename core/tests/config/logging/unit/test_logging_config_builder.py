""" Tests for the project-wide logging configuration builder. """

import os
from unittest.mock import patch
from core.config.logging import LoggingConfigBuilder
from core.testing import LoggedSimpleTestCase


class TestLoggingConfigBuilder(LoggedSimpleTestCase):
    """ Verify the logging builder exposes the expected shared configuration. """

    PROJECT_APPS = ["core", "accounts", "tenancy"]
    LOGGING_ENV_KEYS = ("LOG_LEVEL", "DJANGO_LOG_LEVEL", "CELERY_LOG_LEVEL")

    def test_build_uses_debug_friendly_default_levels(self) -> None:
        """ Verify debug environments default the app logger to DEBUG and Django to INFO. """
        with patch.dict("os.environ", {key: "" for key in self.LOGGING_ENV_KEYS}, clear=False):
            for key in self.LOGGING_ENV_KEYS:
                os.environ.pop(key, None)
            logging_config = LoggingConfigBuilder.build(debug=True, project_apps=self.PROJECT_APPS)

        self.assertEqual("DEBUG", logging_config["root"]["level"])
        self.assertEqual("DEBUG", logging_config["handlers"]["console"]["level"])
        self.assertEqual("INFO", logging_config["loggers"]["django"]["level"])
        self.assertEqual("INFO", logging_config["loggers"]["celery"]["level"])
        self.assertIn("core", logging_config["loggers"])
        self.assertIn("accounts", logging_config["loggers"])
        self.assertIn("tenancy", logging_config["loggers"])

    def test_build_uses_production_friendly_default_levels(self) -> None:
        """ Verify non-debug environments default the app logger to INFO and Django to WARNING. """
        with patch.dict("os.environ", {key: "" for key in self.LOGGING_ENV_KEYS}, clear=False):
            for key in self.LOGGING_ENV_KEYS:
                os.environ.pop(key, None)
            logging_config = LoggingConfigBuilder.build(debug=False, project_apps=self.PROJECT_APPS)

        self.assertEqual("INFO", logging_config["root"]["level"])
        self.assertEqual("INFO", logging_config["handlers"]["console"]["level"])
        self.assertEqual("WARNING", logging_config["loggers"]["django"]["level"])
        self.assertEqual("INFO", logging_config["loggers"]["celery"]["level"])

    def test_build_prefers_environment_level_overrides(self) -> None:
        """ Verify explicit environment variables override the default logger levels. """
        with patch.dict(
            "os.environ",
            {
                "LOG_LEVEL": "warning",
                "DJANGO_LOG_LEVEL": "error",
                "CELERY_LOG_LEVEL": "debug",
            },
            clear=False,
        ):
            logging_config = LoggingConfigBuilder.build(debug=True, project_apps=self.PROJECT_APPS)

        self.assertEqual("WARNING", logging_config["root"]["level"])
        self.assertEqual("WARNING", logging_config["handlers"]["console"]["level"])
        self.assertEqual("WARNING", logging_config["loggers"]["core"]["level"])
        self.assertEqual("ERROR", logging_config["loggers"]["django"]["level"])
        self.assertEqual("DEBUG", logging_config["loggers"]["celery"]["level"])

    def test_build_uses_only_current_runtime_project_apps_as_namespaces(self) -> None:
        """ Verify the project logger namespaces come from the explicit project app list. """
        logging_config = LoggingConfigBuilder.build(
            debug=True,
            project_apps=["core", "accounts", "tenancy"],
        )

        self.assertIn("core", logging_config["loggers"])
        self.assertIn("accounts", logging_config["loggers"])
        self.assertIn("tenancy", logging_config["loggers"])
        self.assertNotIn("front", logging_config["loggers"])
        self.assertNotIn("quotation", logging_config["loggers"])
        self.assertNotIn("storages", logging_config["loggers"])
