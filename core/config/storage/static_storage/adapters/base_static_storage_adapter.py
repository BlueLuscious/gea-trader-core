""" Base types and shared contract for static storage adapters. """

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StaticStorageConfig:
    """ Represent resolved static storage settings for the current environment. """

    provider: str
    static_url: str
    static_root: Path
    storages: dict[str, dict[str, Any]]
    extra_apps: list[str]
    extra_middleware: list[str]


class BaseStaticStorageAdapter(ABC):
    """ Define the contract for static storage provider adapters. """

    provider: str

    def get_static_url(self) -> str:
        """ Resolve the fallback static URL from environment variables.

        Returns:
            str: The configured static URL or the default local value.
        """
        return os.environ.get("STATIC_URL", "/static/")

    def get_static_root(self, base_dir: Path) -> Path:
        """ Resolve the static root path from environment variables.

        Args:
            base_dir: Project base directory used to resolve local paths.

        Returns:
            Path: The configured static root path.
        """
        return base_dir / os.environ.get("STATIC_ROOT", "staticfiles")

    @abstractmethod
    def build(self, base_dir: Path) -> StaticStorageConfig:
        """ Build the static storage configuration for this provider.

        Args:
            base_dir: Project base directory used to resolve local paths.

        Returns:
            StaticStorageConfig: Resolved static storage configuration.
        """
