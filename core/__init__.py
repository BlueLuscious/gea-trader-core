""" Project package bootstrap exports. """

from core.celery import celery_app

__all__: list[str] = ["celery_app"]
