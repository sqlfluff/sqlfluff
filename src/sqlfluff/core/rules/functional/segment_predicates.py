"""Defines commonly used segment predicates for rule writers.

For consistency, all the predicates in this module are implemented as functions
returning functions. This avoids rule writers having to remember the
distinction between normal functions and functions returning functions.

This is not necessarily a complete set of predicates covering all possible
requirements. Rule authors can define their own predicates as needed, either
as regular functions, `lambda`, etc.
"""
from typing import Callable, Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.functional.raw_file_slices import RawFileSlices
from sqlfluff.core.templaters.base import TemplatedFile


def is_type(*seg_type: str) -> Callable[[BaseSegment], bool]:
    """Returns a function that determines if segment is one of the types."""

    def _(segment: BaseSegment):
        return segment.is_type(*seg_type)

    return _


def is_name(*seg_name: str) -> Callable[[BaseSegment], bool]:
    """Returns a function that determines if segment is one of the names."""

    def _(segment: BaseSegment):
        return segment.is_name(*seg_name)

    return _


def is_keyword(*keyword_name) -> Callable[[BaseSegment], bool]:
    """Returns a function that determines if it's a matching keyword."""
    return and_(is_type("keyword"), is_name(*keyword_name))


def is_code() -> Callable[[BaseSegment], bool]:
    """Returns a function that checks if segment is code."""

    def _(segment: BaseSegment) -> bool:
        return segment.is_code

    return _


def is_comment() -> Callable[[BaseSegment], bool]:
    """Returns a function that checks if segment is comment."""

    def _(segment: BaseSegment) -> bool:
        return segment.is_comment

    return _


def is_expandable() -> Callable[[BaseSegment], bool]:
    """Returns a function that checks if segment is expandable."""

    def _(segment: BaseSegment) -> bool:
        return segment.is_expandable

    return _


def is_meta() -> Callable[[BaseSegment], bool]:
    """Returns a function that checks if segment is meta."""

    def _(segment: BaseSegment) -> bool:
        return segment.is_meta

    return _


def is_raw() -> Callable[[BaseSegment], bool]:
    """Returns a function that checks if segment is raw."""

    def _(segment: BaseSegment) -> bool:
        return segment.is_raw()

    return _


def is_whitespace() -> Callable[[BaseSegment], bool]:
    """Returns a function that checks if segment is whitespace."""

    def _(segment: BaseSegment) -> bool:
        return segment.is_whitespace

    return _


def get_type() -> Callable[[BaseSegment], str]:
    """Returns a function that gets segment type."""

    def _(segment: BaseSegment) -> str:
        return segment.get_type()

    return _


def get_name() -> Callable[[BaseSegment], str]:
    """Returns a function that gets segment name."""

    def _(segment: BaseSegment) -> str:
        return segment.get_name()

    return _


def and_(*functions: Callable[[BaseSegment], bool]) -> Callable[[BaseSegment], bool]:
    """Returns a function that computes the functions and-ed together."""

    def _(segment: BaseSegment):
        return all(function(segment) for function in functions)

    return _


def or_(*functions: Callable[[BaseSegment], bool]) -> Callable[[BaseSegment], bool]:
    """Returns a function that computes the functions or-ed together."""

    def _(segment: BaseSegment):
        return any(function(segment) for function in functions)

    return _


def not_(fn: Callable[[BaseSegment], bool]) -> Callable[[BaseSegment], bool]:
    """Returns a function that computes: not fn()."""

    def _(segment: BaseSegment):
        return not fn(segment)

    return _


def raw_slices(
    segment: BaseSegment,
    templated_file: Optional[TemplatedFile],
) -> RawFileSlices:
    """Returns raw slices for a segment."""
    if not templated_file:
        raise ValueError('raw_slices: "templated_file" parameter is required.')
    return RawFileSlices(
        *templated_file.raw_slices_spanning_source_slice(
            segment.pos_marker.source_slice
        ),
        templated_file=templated_file
    )
