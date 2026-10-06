"""Classes for managing linter output, used with OutputStreamFormatter."""

import abc
import os
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional

import click
from tqdm import tqdm

from sqlfluff.core import FluffConfig
from sqlfluff.core.types import FormatType


class OutputKind(Enum):
    """Semantic categories used to decide whether CLI output is emitted."""

    PAYLOAD = auto()
    DIAGNOSTIC = auto()
    ACTION = auto()
    STATUS = auto()
    PROGRESS = auto()
    VERBOSE = auto()


@dataclass(frozen=True)
class OutputPolicy:
    """Control CLI output independently from result and exit-code handling."""

    verbosity: int = 0
    quiet: bool = False
    machine_output: bool = False

    def allows(self, kind: OutputKind, *, minimum_verbosity: int = 0) -> bool:
        """Return whether an output category should be emitted."""
        if kind is OutputKind.PAYLOAD:
            return True
        if self.machine_output:
            return False
        if kind in (OutputKind.DIAGNOSTIC, OutputKind.ACTION):
            return True
        return not self.quiet and self.verbosity >= minimum_verbosity


class OutputStream(abc.ABC):
    """Base class for linter output stream."""

    def __init__(self, config: FluffConfig, context: Any = None) -> None:
        self.config = config

    def write(self, message: str) -> None:
        """Write message to output."""
        raise NotImplementedError  # pragma: no cover

    def close(self) -> None:
        """Close output stream."""
        pass


class TqdmOutput(OutputStream):
    """Outputs to stdout, coordinates to avoid conflict with tqdm.

    It may happen that progressbar conflicts with extra printing. Nothing very
    serious happens then, except that there is printed (not removed) progressbar
    line. The `external_write_mode` allows to disable tqdm for writing time.
    """

    def __init__(self, config: FluffConfig) -> None:
        super().__init__(config)

    def write(self, message: str) -> None:
        """Write message to stdout."""
        with tqdm.external_write_mode():
            click.echo(message=message, color=self.config.get("color"))


class FileOutput(OutputStream):
    """Outputs to a specified file."""

    def __init__(self, config: FluffConfig, output_path: str) -> None:
        super().__init__(config)
        self.file = open(output_path, "w")

    def write(self, message: str) -> None:
        """Write message to output_path."""
        print(message, file=self.file)

    def close(self) -> None:
        """Close output file."""
        self.file.close()


def make_output_stream(
    config: FluffConfig,
    format: Optional[str] = None,
    output_path: Optional[str] = None,
) -> OutputStream:
    """Create and return appropriate OutputStream instance."""
    if format is None or format == FormatType.human.value:
        if not output_path:
            # Human-format output to stdout.
            return TqdmOutput(config)
        else:
            # Human-format output to a file.
            return FileOutput(config, output_path)
    else:
        # Discard human output as not required
        return FileOutput(config, os.devnull)
