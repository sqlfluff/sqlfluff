"""Adapter to convert Rust parser output (RsNode) to Python BaseSegment tree.

This module provides the bridge between the Rust parser and Python linter infrastructure.
The Rust parser returns RsNode objects, but the linter expects BaseSegment objects.
"""

from typing import TYPE_CHECKING, Optional

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.parser.segments.base import BaseSegment, UnparsableSegment
from sqlfluff.core.parser.segments.keyword import LiteralKeywordSegment
from sqlfluff.core.parser.segments.meta import ImplicitIndent
from sqlfluff.core.parser.segments.raw import RawSegment
from sqlfluff.core.templaters.base import TemplatedFile

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.config import FluffConfig
    from sqlfluffrs import RsNode, RsToken


def _get_segment_type_map(base_class: type) -> dict[str, type[RawSegment]]:
    """Dynamically create a map of segment types to their subclasses.

    This mirrors the implementation in lexer.py to map token types
    to their corresponding segment classes (WordSegment, LiteralSegment, etc.).
    """
    segment_map = {}
    for subclass in base_class.__subclasses__():
        if subclass is LiteralKeywordSegment or subclass is ImplicitIndent:
            continue
        if hasattr(subclass, "type") and subclass.type:
            segment_map[subclass.type] = subclass
        # Recursively add subclasses of subclasses
        segment_map.update(_get_segment_type_map(subclass))
    return segment_map


def _is_valid_segment_class(segment_name: str, dialect: Dialect) -> bool:
    """Check if a name refers to a valid segment class in the dialect.

    This is the authoritative check - it queries the dialect's _library to determine
    if the name refers to an actual segment class (vs a grammar element).

    Args:
        segment_name: The name to check (e.g., "AsAliasOperatorSegment", "base", "SelectableGrammar")
        config: The FluffConfig (provides access to dialect)

    Returns:
        True if the name is a valid segment class, False otherwise (grammar or not found)
    """
    item = dialect._library.get(segment_name)

    # Must be a type (class) and a BaseSegment subclass
    return item is not None and isinstance(item, type) and issubclass(item, BaseSegment)


def get_segment_class_by_name(
    segment_name: str, dialect: "Dialect"
) -> type[BaseSegment]:
    """Get a segment class by its exact class name from the dialect.

    Args:
        segment_name: The segment CLASS name (e.g., "AsAliasOperatorSegment")
        dialect: The FluffConfig (provides access to dialect)

    Returns:
        The segment class

    Raises:
        ValueError: If the segment class is not found in the dialect,
                    or if the name refers to a grammar instead of a segment class
    """
    # First check if it's a valid segment class
    if _is_valid_segment_class(segment_name, dialect):
        return dialect.get_segment(segment_name)

    # Not a valid segment class - provide helpful error message
    if segment_name.endswith("Grammar"):
        raise ValueError(f"'{segment_name}' is a grammar, not a segment class")

    item = dialect._library.get(segment_name)

    if item is None:
        raise ValueError(f"Segment '{segment_name}' not found in dialect")

    raise ValueError(
        f"'{segment_name}' is not a segment class (got {type(item).__name__})"
    )
