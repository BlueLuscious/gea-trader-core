""" Build project-wide Celery Beat schedule definitions. """

from typing import Any


class CeleryBeatScheduleBuilder:
    """ Build code-based Celery Beat schedule definitions for the project runtime. """

    @classmethod
    def build(cls) -> dict[str, dict[str, Any]]:
        """ Build the Celery Beat schedule mapping.

        Returns:
            dict[str, dict[str, Any]]: Celery Beat schedule entries keyed by schedule name.
        """
        return {}
