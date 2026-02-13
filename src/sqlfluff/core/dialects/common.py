"""Common classes for dialects to use."""

from typing import NamedTuple, Optional

from sqlfluff.core.parser import BaseSegment

# Dialect metadata set name for reference-related capabilities.
REFERENCE_FEATURES_SET = "reference_features"
# Dialect supports dot-access style references (e.g. table.column.field).
REFERENCE_FEATURE_DOT_ACCESS = "dot_access"
# Dialect has ambiguous struct-style qualification for RF03 defaults.
REFERENCE_FEATURE_STRUCT_QUALIFICATION_AMBIGUITY = (
    "struct_qualification_ambiguity"
)


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
    column_reference_segments: list[BaseSegment]
