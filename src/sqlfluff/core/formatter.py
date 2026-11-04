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
from typing import TYPE_CHECKING, Optional

from sqlfluff.core.types import Color

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.config import FluffConfig
    from sqlfluff.core.linter import LintedFile


class FormatterInterface(ABC):
    """Generic formatter interface."""

    @abstractmethod
    def dispatch_persist_filename(self, filename: str, result: str) -> None:
        """Called after a formatted file as been persisted to disk."""
        ...

    @abstractmethod
    def dispatch_lint_header(self, fname: str, rules: list[str]) -> None:
        """Dispatch the header displayed before linting."""
        ...

    @abstractmethod
    def dispatch_file_violations(
        self,
        fname: str,
        linted_file: "LintedFile",
        only_fixable: bool,
        warn_unused_ignores: bool,
    ) -> None:
        """Dispatch any violations found in a file."""
        ...

    @abstractmethod
    def dispatch_dialect_warning(self, dialect: str) -> None:
        """Dispatch a warning for dialects."""
        ...

    @abstractmethod
    def dispatch_template_header(
        self,
        fname: str,
        linter_config: "FluffConfig",
        file_config: Optional["FluffConfig"],
    ) -> None:
        """Dispatch the header displayed before templating."""
        ...

    def dispatch_config_diff(
        self,
        fname: str,
        file_config: "FluffConfig",
        linter_config: "FluffConfig",
    ) -> None:
        """Dispatch the difference between the file and root config.

        Called when a file's effective config differs from the root
        config (e.g. from a nested config file or in-file config
        directives). The default implementation does nothing.
        """
        return None

    @abstractmethod
    def dispatch_parse_header(self, fname: str) -> None:
        """Dispatch the header displayed before parsing."""
        ...

    @abstractmethod
    def dispatch_processing_header(self, processes: int) -> None:
        """Dispatch the header displayed before linting."""
        ...

    @abstractmethod
    def dispatch_path(self, path: str) -> None:
        """Dispatch paths for display."""
        ...

    @abstractmethod
    def colorize(self, s: str, color: Optional[Color] = None) -> str:
        """Optionally use ANSI colour codes to colour a string."""
        ...
