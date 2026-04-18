""" Base types and shared contract for media storage adapters. """

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MediaStorageConfig:
    """ Represent resolved media storage settings for the current environment. """

    provider: str
    media_url: str
    media_root: Path
    storages: dict[str, dict[str, Any]]
    extra_apps: list[str]


class BaseMediaStorageAdapter(ABC):
    """ Define the contract for media storage provider adapters. """

    provider: str

    def get_media_url(self) -> str:
        """ Resolve the fallback media URL from environment variables.

        Returns:
            str: The configured media URL or the default local value.
        """
        return os.environ.get("MEDIA_URL", "/media/")

    def get_media_root(self, base_dir: Path) -> Path:
        """ Resolve the media root path from environment variables.

        Args:
            base_dir: Project base directory used to resolve local paths.

        Returns:
            Path: The configured media root path.
        """
        return base_dir / os.environ.get("MEDIA_ROOT", "media")

    @abstractmethod
    def build(self, base_dir: Path) -> MediaStorageConfig:
        """ Build the media storage configuration for this provider.

        Args:
            base_dir: Project base directory used to resolve local paths.

        Returns:
            MediaStorageConfig: Resolved media storage configuration.
        """
