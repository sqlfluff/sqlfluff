"""Defines the formatter interface which can be used by the CLI.

The linter module provides an optional formatter input which effectively
allows callbacks at various points of the linting process. This is primarily
to allow printed output at various points by the CLI, but could also be used
for logging our other processes looking to report back as the linting process
continues.

In this module we only define the interface. Any modules wishing to use the
interface should override with their own implementation.
"""

from abc import ABC, abstractmethod


class FormatterInterface(ABC):
    """Generic formatter interface."""

    @abstractmethod
    def dispatch_persist_filename(self, filename: str, result: str) -> None:
        """Called after a formatted file as been persisted to disk."""
        ...
