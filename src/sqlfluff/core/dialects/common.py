"""Common classes for dialects to use."""

from typing import NamedTuple, Optional

from sqlfluff.core.parser import BaseSegment


class AliasInfo(NamedTuple):
    """Details about a table alias."""

    ref_str: str  # Name given to the alias
    segment: BaseSegment  # Identifier segment containing the name
    aliased: bool
    from_expression_element: BaseSegment
    alias_expression: Optional[BaseSegment]
    object_reference: Optional[BaseSegment]
