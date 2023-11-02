"""CLI helper utilities."""

import sys
import textwrap
from collections import abc
from functools import cached_property
from typing import Any, Callable, Dict, List

from sqlfluff import __version__ as pkg_version


def get_python_version() -> str:
    """Get the current python version as a string."""
    return "{0[0]}.{0[1]}.{0[2]}".format(sys.version_info)


def get_python_implementation() -> str:
    """Get the current python implementation as a string.

    This is useful if testing in pypy or similar.
    """
    return sys.implementation.name


def get_package_version() -> str:
    """Get the current version of the sqlfluff package."""
    return pkg_version


def wrap_elem(s: str, width: int) -> List[str]:
    """Wrap a string into a list of strings all less than <width>."""
    return textwrap.wrap(s, width=width)


def wrap_field(
    label: str, val: str, width: int, max_label_width: int = 10, sep_char: str = ": "
) -> Dict[str, Any]:
    """Wrap a field (label, val).

    Returns:
        A dict of {label_list, val_list, sep_char, lines}

    """
    if len(label) > max_label_width:
        label_list = wrap_elem(label, width=max_label_width)
        label_width = max(len(line) for line in label_list)
    else:
        label_width = len(label)
        label_list = [label]

    max_val_width = width - len(sep_char) - label_width
    val_list = []
    for v in val.split("\n"):
        val_list.extend(wrap_elem(v, width=max_val_width))

    return dict(
        label_list=label_list,
        val_list=val_list,
        sep_char=sep_char,
        lines=max(len(label_list), len(val_list)),
        label_width=label_width,
        val_width=max_val_width,
    )


def pad_line(s: str, width: int, align: str = "left") -> str:
    """Pad a string with a given alignment to a specific width with spaces."""
    gap = width - len(s)
    if gap <= 0:
        return s
    elif align == "left":
        return s + (" " * gap)
    elif align == "right":
        return (" " * gap) + s
    else:
        raise ValueError(f"Unknown alignment: {align}")  # pragma: no cover


class LazySequence(abc.Sequence):
    """A Sequence which only populates on the first access.

    This is useful for being able to define sequences within
    the click cli decorators, but that don't trigger their
    contents until first called.
    """

    def __init__(self, getter=Callable[[], abc.Sequence]):
        self._getter = getter

    @cached_property
    def _sequence(self) -> abc.Sequence:
        return self._getter()

    def __getitem__(self, key):
        return self._sequence[key]

    def __len__(self):
        return len(self._sequence)
