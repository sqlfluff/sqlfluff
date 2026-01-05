"""Adapter to convert Rust parser output (RsNode) to Python BaseSegment tree.

This module provides the bridge between the Rust parser and Python linter
infrastructure. The Rust parser returns RsNode objects, but the linter expects
BaseSegment objects.
"""

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.parser.segments.base import BaseSegment


def _is_valid_segment_class(segment_name: str, dialect: Dialect) -> bool:
    """Check if a name refers to a valid segment class in the dialect.

    This is the authoritative check - it queries the dialect's _library to determine
    if the name refers to an actual segment class (vs a grammar element).

    Args:
        segment_name: The name to check (e.g., "AsAliasOperatorSegment", "base",
            "SelectableGrammar")
        dialect: The Dialect instance to check against

    Returns:
        True if the name is a valid segment class, False otherwise (grammar or
        not found).
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
        dialect: The dialect instance (provides access to dialect library)

    Returns:
        The segment class

    Raises:
        ValueError: If the segment class is not found in the dialect,
                    or if the name refers to a grammar instead of a segment class
    """
    # Check if it's a valid segment class
    if _is_valid_segment_class(segment_name, dialect):
        return dialect.get_segment(segment_name)

    # Not a valid segment class
    raise ValueError(f"Segment '{segment_name}' not found or is not a segment class")
