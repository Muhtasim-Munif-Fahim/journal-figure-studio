"""Version information for journal-figure-studio."""

from __future__ import annotations

__version__ = "0.2.0"

__all__ = ["__version__", "__title__", "__description__", "__author__", "__email__", "__license__", "get_version"]
__title__ = "journal-figure-studio"
__description__ = "Reproducible, publication-ready academic figure packages"
__author__ = "Muhtasim Munif Fahim"
__email__ = "s1911024120@ru.ac.bd"
__license__ = "MIT"


def get_version() -> str:
    return __version__
