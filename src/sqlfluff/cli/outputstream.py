"""Classes for managing linter output, used with CallbackFormatter."""
import abc
import os
from typing import Any, Optional

import click
from tqdm import tqdm

from sqlfluff.core import FluffConfig
from sqlfluff.core.enums import FormatType


class OutputStream(abc.ABC):
    """Base class for linter output stream."""

    def __init__(self, config: FluffConfig, context: Any = None):
        self.config = config
        self.context = context

    def __call__(self, message: str) -> None:
        """Write message to output."""
        pass

    def __enter__(self):
        if self.context:
            self.context.__enter__()

    def __exit__(self, type, value, traceback):
        if self.context:
            self.context.__exit__()


class TqdmOutput(OutputStream):
    """Outputs to stdout, coordinates to avoid conflict with tqdm.

    It may happen that progressbar conflicts with extra printing. Nothing very
    serious happens then, except that there is printed (not removed) progressbar
    line. The `external_write_mode` allows to disable tqdm for writing time.
    """

    def __init__(self, config: FluffConfig):
        super().__init__(config, context=tqdm.external_write_mode())

    def __call__(self, message: str) -> None:
        """Write message to stdout."""
        click.echo(message=message, color=self.config.get("color"))


class FileOutput(OutputStream):
    """Outputs to a specified file."""

    def __init__(self, config: FluffConfig, output_path: str):
        super().__init__(config, context=open(output_path, "w"))

    def __call__(self, message: str) -> None:
        """Write message to output_path."""
        print(message, file=self.context)


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
        # Discard output
        return FileOutput(config, os.devnull)
