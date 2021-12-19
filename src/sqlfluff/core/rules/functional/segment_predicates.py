"""Defines commonly used segment predicates for rule writers.

This is not necessarily a complete set of predicates covering all possible
requirements. Rule authors can define their own predicates as needed.
"""
from operator import attrgetter as attrgetter
from typing import Any, Callable

from sqlfluff.core.parser import BaseSegment


def is_code(segment: BaseSegment) -> bool:
    """Check if segment is code."""
    return segment.is_code


def is_comment(segment: BaseSegment) -> bool:
    """Check if segment is comment."""
    return segment.is_comment


def is_expandable(segment: BaseSegment) -> bool:
    """Check if segment is expandable."""
    return segment.is_expandable


def is_meta(segment: BaseSegment) -> bool:
    """Check if segment is meta."""
    return segment.is_meta


def is_raw(segment: BaseSegment) -> bool:
    """Check if segment is raw."""
    return segment.is_raw()


def is_whitespace(segment: BaseSegment) -> bool:
    """Check if segment is whitespace."""
    return segment.is_whitespace


def get_type(segment: BaseSegment) -> str:
    """Returns segment type."""
    return segment.get_type()


def and_(
    fn1: Callable[[BaseSegment], bool], fn2: Callable[[BaseSegment], bool]
) -> Callable[[BaseSegment], bool]:  # pragma: no cover
    """Returns a function that computes: fn1() and fn2()."""

    def _(segment: BaseSegment):
        return fn1(segment) and fn2(segment)

    return _


def or_(
    fn1: Callable[[BaseSegment], bool], fn2: Callable[[BaseSegment], bool]
) -> Callable[[BaseSegment], bool]:
    """Returns a function that computes: fn1() or fn2()."""

    def _(segment: BaseSegment):
        return fn1(segment) or fn2(segment)

    return _


def not_(
    fn: Callable[[BaseSegment], bool]
) -> Callable[[BaseSegment], bool]:  # pragma: no cover
    """Returns a function that computes: not fn()."""

    def _(segment: BaseSegment):
        return not fn(segment)

    return _


def attr(*attrs: str) -> Callable[[Any], bool]:
    """Returns a function that gets an attribute of an object.

    This function is useful for creating Predicates for use by
    surrogate object methods.
    """
    # TODO: If the attribute is not defined, consider returning False.
    getter = attrgetter(*attrs)

    def fn(obj: Any) -> bool:
        return bool(getter(obj))

    return fn
