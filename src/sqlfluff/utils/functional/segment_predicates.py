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
from sqlfluff.core.templaters.base import TemplatedFile
from sqlfluff.utils.functional.raw_file_slices import RawFileSlices
from sqlfluff.utils.functional.templated_file_slices import TemplatedFileSlices


def raw_is(*raws: str) -> Callable[[BaseSegment], bool]:  # pragma: no cover
    """Returns a function that determines if segment matches one of the raw inputs."""

    def _(segment: BaseSegment) -> bool:
        return segment.raw in raws

    return _


def raw_upper_is(*raws: str) -> Callable[[BaseSegment], bool]:
    """Returns a function that determines if segment matches one of the raw inputs."""

    def _(segment: BaseSegment) -> bool:
        return segment.raw_upper in raws

    return _


def is_type(*seg_type: str) -> Callable[[BaseSegment], bool]:
    """Returns a function that determines if segment is one of the types."""

    def _(segment: BaseSegment) -> bool:
        return segment.is_type(*seg_type)

    return _


def is_keyword(*keyword_name: str) -> Callable[[BaseSegment], bool]:
    """Returns a function that determines if it's a matching keyword."""
    return and_(
        is_type("keyword"), raw_upper_is(*[raw.upper() for raw in keyword_name])
    )


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


def is_templated() -> Callable[[BaseSegment], bool]:  # pragma: no cover
    """Returns a function that checks if segment is templated."""

    def _(segment: BaseSegment) -> bool:
        return segment.is_templated

    return _


def get_type() -> Callable[[BaseSegment], str]:
    """Returns a function that gets segment type."""

    def _(segment: BaseSegment) -> str:
        return segment.get_type()

    return _


def and_(*functions: Callable[[BaseSegment], bool]) -> Callable[[BaseSegment], bool]:
    """Returns a function that computes the functions and-ed together."""

    def _(segment: BaseSegment) -> bool:
        return all(function(segment) for function in functions)

    return _


def or_(*functions: Callable[[BaseSegment], bool]) -> Callable[[BaseSegment], bool]:
    """Returns a function that computes the functions or-ed together."""

    def _(segment: BaseSegment) -> bool:
        return any(function(segment) for function in functions)

    return _


def not_(fn: Callable[[BaseSegment], bool]) -> Callable[[BaseSegment], bool]:
    """Returns a function that computes: not fn()."""

    def _(segment: BaseSegment) -> bool:
        return not fn(segment)

    return _


def raw_slices(
    segment: BaseSegment,
    templated_file: Optional[TemplatedFile],
) -> RawFileSlices:  # pragma: no cover
    """Returns raw slices for a segment."""
    if not templated_file:
        raise ValueError(
            'raw_slices: "templated_file" parameter is required.'
        )  # pragma: no cover
    if not segment.pos_marker:
        raise ValueError(
            'raw_slices: "segment" parameter must have pos_marker set.'
        )  # pragma: no cover
    return RawFileSlices(
        *templated_file.raw_slices_spanning_source_slice(
            segment.pos_marker.source_slice
        ),
        templated_file=templated_file,
    )


def templated_slices(
    segment: BaseSegment,
    templated_file: Optional[TemplatedFile],
) -> TemplatedFileSlices:
    """Returns raw slices for a segment."""
    if not templated_file:
        raise ValueError(
            'templated_slices: "templated_file" parameter is required.'
        )  # pragma: no cover
    if not segment.pos_marker:
        raise ValueError(
            'templated_slices: "segment" parameter must have pos_marker set.'
        )  # pragma: no cover
    # :TRICKY: We don't use _find_slice_indices_of_templated_pos() here because
    # it treats TemplatedFileSlice.templated_slice.stop as inclusive, not
    # exclusive. Other parts of SQLFluff rely on this behaviour, but we don't
    # want it. It's easy enough to do this ourselves.
    start = segment.pos_marker.templated_slice.start
    stop = segment.pos_marker.templated_slice.stop
    templated_slices = [
        slice_
        for slice_ in templated_file.sliced_file
        if (stop > slice_.templated_slice.start and start < slice_.templated_slice.stop)
    ]
    return TemplatedFileSlices(*templated_slices, templated_file=templated_file)
