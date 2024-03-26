"""Common classes for dialects to use."""

from typing import List, NamedTuple, Optional

from sqlfluff.core.parser import BaseSegment


class AliasInfo(NamedTuple):
    """Details about a table alias."""

    ref_str: str  # Name given to the alias
    segment: Optional[BaseSegment]  # Identifier segment containing the name
    aliased: bool
    from_expression_element: BaseSegment
    alias_expression: Optional[BaseSegment]
    object_reference: Optional[BaseSegment]


class ColumnAliasInfo(NamedTuple):
    """Details about a column alias."""

    alias_identifier_name: str
    aliased_segment: BaseSegment
    column_reference_segments: List[BaseSegment]
