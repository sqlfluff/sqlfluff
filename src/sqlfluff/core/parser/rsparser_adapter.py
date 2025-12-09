"""Adapter to convert Rust parser output (RsNode) to Python BaseSegment tree.

This module provides the bridge between the Rust parser and Python linter infrastructure.
The Rust parser returns RsNode objects, but the linter expects BaseSegment objects.
"""

from typing import TYPE_CHECKING, Optional

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


# Build the segment type map once at module load
_SEGMENT_TYPES = _get_segment_type_map(RawSegment)

# DEPRECATED: This mapping is no longer needed as of the breaking changes to Node structure.
# The Rust parser now includes a segment_type field in Token nodes that provides the
# base type directly, computed using the type_mapping module in Rust.
# This dictionary is kept for reference but should be removed in a future cleanup.
#
# Map grammar-specific token types to segment class types
# The Rust parser gives us semantic types like 'naked_identifier' but
# we need to map these to segment class types like 'identifier'
_GRAMMAR_TYPE_TO_SEGMENT_TYPE = {
    # Identifier types -> IdentifierSegment
    "naked_identifier": "identifier",
    "quoted_identifier": "identifier",
    # Literal types -> LiteralSegment
    "quoted_literal": "literal",
    "single_quote": "literal",
    "double_quote": "literal",
    "numeric_literal": "literal",
    "integer_literal": "literal",
    "float_literal": "literal",
    # Symbol types
    "comma": "symbol",
    "dot": "symbol",
    "semicolon": "symbol",
    "colon": "symbol",
    "raw": "symbol",  # Raw symbols like comma, dot, etc.
    "raw_comparison_operator": "symbol",  # Comparison operators like =, >, <
    # Comparison/operator types
    "equals": "comparison_operator",
    "not_equals": "comparison_operator",
    "less_than": "comparison_operator",
    "greater_than": "comparison_operator",
    "less_than_or_equal": "comparison_operator",
    "greater_than_or_equal": "comparison_operator",
    # These already map correctly
    "keyword": "keyword",
    "word": "word",
    "whitespace": "whitespace",
    "newline": "newline",
    "literal": "literal",
    "symbol": "symbol",
    "comment": "comment",
    "end_of_file": "end_of_file",
    "identifier": "identifier",
    "comparison_operator": "comparison_operator",
}


def _map_grammar_type_to_segment_type(token_type: str) -> str:
    """DEPRECATED: Map grammar-specific token types to segment class types.

    This function is no longer needed as of the breaking changes to Node structure.
    The Rust parser now returns segment_type directly in token_info().
    Kept for backward compatibility but should be removed in future cleanup.

    The Rust parser provides semantic types (e.g., 'naked_identifier')
    but segment classes use base types (e.g., 'identifier').
    """
    return _GRAMMAR_TYPE_TO_SEGMENT_TYPE.get(token_type, token_type)


def rsnode_to_segment(
    node: "RsNode",
    tokens: list["RsToken"],
    config: "FluffConfig",
    tf: Optional[TemplatedFile] = None,
) -> Optional[BaseSegment]:
    """Convert a Rust parser RsNode to a Python BaseSegment.

    Args:
        node: The RsNode from Rust parser
        tokens: The list of tokens (needed to reconstruct RawSegments)
        config: The FluffConfig (provides access to dialect segment classes)
        tf: Optional TemplatedFile for position marker reconstruction

    Returns:
        BaseSegment tree corresponding to the RsNode, or None if empty
    """
    node_type = node.node_type

    # Handle empty nodes
    if node_type == "empty":
        return None

    # Handle token nodes (leaf nodes)
    if node_type in ("token", "whitespace", "newline", "end_of_file"):
        token_info = node.token_info()
        if token_info is None:
            raise ValueError(f"Token node has no token_info: {node_type}")

        # token_info now returns (token_type, segment_type, raw, token_idx)
        # - token_type: semantic type from the lexer (e.g., 'naked_identifier', 'keyword')
        # - segment_type: base type for class lookup (e.g., 'identifier', 'keyword')
        # Both are already computed by Rust using the type_mapping module
        token_type, segment_type, _raw, token_idx = token_info

        # Get the original token to reconstruct segment with correct type
        if token_idx >= len(tokens):
            raise ValueError(
                f"Token index {token_idx} out of range (max {len(tokens) - 1})"
            )

        original_token = tokens[token_idx]

        # Use segment_type (already computed by Rust) for segment class lookup
        # No need for _map_grammar_type_to_segment_type anymore
        segment_class = _SEGMENT_TYPES.get(segment_type, RawSegment)

        # Create segment with the semantic type from Rust parser
        # The token_type (e.g., 'naked_identifier') goes into instance_types
        # so is_type('naked_identifier') works, while the segment class
        # (e.g., IdentifierSegment) provides class-level type checking
        #
        # Note: Some segment classes (e.g., MetaSegment) don't support type_override
        # because they don't have instance_types. Check if the method accepts it.
        import inspect

        sig = inspect.signature(segment_class.from_rstoken)
        if "type_override" in sig.parameters:
            return segment_class.from_rstoken(
                original_token, tf, type_override=token_type
            )
        else:
            return segment_class.from_rstoken(original_token, tf)

    # Handle unparsable segments
    if node_type == "unparsable":
        # Get expected message and children
        # Note: RsNode doesn't expose expected_message yet, we'll need to add that
        children_nodes = node.children()
        if children_nodes is None:
            children_nodes = []

        children_segments = [
            rsnode_to_segment(child, tokens, config, tf) for child in children_nodes
        ]
        children_segments = [s for s in children_segments if s is not None]

        if not children_segments:
            return None

        return UnparsableSegment(
            tuple(children_segments), expected="Unparsable content from Rust parser"
        )

    # Handle Ref nodes (most segment types)
    if node_type == "ref":
        ref_info = node.ref_info()
        if ref_info is None:
            raise ValueError("Ref node has no ref_info")

        # ref_info now returns (name, segment_type, segment_class_name) where:
        # - name: the reference name from the grammar (e.g., "AsAliasOperatorSegment" or "SelectStatementGrammar")
        # - segment_type: the segment's type attribute (e.g., "alias_operator"), or None for grammars
        # - segment_class_name: explicit Python class name (e.g., "KeywordSegment"), or None for grammars
        # The segment_class_name field is the key improvement - when it's None, we know this is a
        # grammar reference and should return children unwrapped. When it's set, we wrap in that class.
        _ref_name, segment_type, segment_class_name = ref_info

        # Get the child node
        children_nodes = node.children()
        if children_nodes is None or len(children_nodes) == 0:
            return None

        # Convert child
        child_segment = rsnode_to_segment(children_nodes[0], tokens, config, tf)
        if child_segment is None:
            return None

        # Check if child_segment is a _SegmentTuple (multiple children from container)
        if (
            hasattr(child_segment, "segments")
            and hasattr(child_segment, "__class__")
            and child_segment.__class__.__name__ == "_SegmentTuple"
        ):
            # Unwrap the tuple - these are the actual child segments
            child_segments = child_segment.segments
        elif isinstance(child_segment, BaseSegment):
            child_segments = (child_segment,)
        else:
            # Shouldn't happen, but handle gracefully
            return child_segment

        # If segment class name is specified, wrap the children in that segment type
        # Note: Use segment_class_name (the actual class name like "AsAliasOperatorSegment")
        # NOT segment_type (the type attribute like "alias_operator")
        #
        # The Rust parser provides segment_class_name based on heuristics (name patterns),
        # but we need to validate it against the dialect's actual segment class registry.
        # If the name isn't a valid segment class, treat the Ref as a grammar (transparent).
        segment_class = None
        if segment_class_name and _is_valid_segment_class(segment_class_name, config):
            try:
                segment_class = _get_segment_class_by_name(segment_class_name, config)
            except ValueError:
                # Class name lookup failed
                # Try using segment_type instead (e.g., 'file' -> FileSegment)
                if segment_type:
                    try:
                        segment_class = _get_segment_class(segment_type, config)
                    except ValueError:
                        pass
        elif segment_type and not segment_class_name:
            # No segment_class_name (Rust identified as grammar), but we have segment_type
            # Try to look up by segment_type (e.g., 'file' -> FileSegment)
            try:
                segment_class = _get_segment_class(segment_type, config)
            except ValueError:
                pass

        if segment_class:
            # Filter to real segments only
            real_segments = [s for s in child_segments if isinstance(s, BaseSegment)]

            # CRITICAL FIX: Strip leading AND trailing non-code segments
            # Python parser doesn't include leading/trailing comments/ws/nl in parsed segments
            # They belong at the parent level, not inside the segment.
            # We collect the stripped segments to return as siblings.
            #
            # EXCEPTION: For FileSegment (segment_type == "file"), we keep all segments
            # because the file is the root and there's no parent to return siblings to.
            from sqlfluff.core.parser.segments.common import (
                CommentSegment,
                NewlineSegment,
                WhitespaceSegment,
            )

            # Only strip for non-file segments
            is_file_segment = segment_type == "file"
            leading_non_code = []
            trailing_non_code = []

            if not is_file_segment:
                # Strip leading non-code segments
                while real_segments and isinstance(
                    real_segments[0],
                    (WhitespaceSegment, NewlineSegment, CommentSegment),
                ):
                    leading_non_code.append(real_segments.pop(0))

                # Strip trailing non-code segments
                while real_segments and isinstance(
                    real_segments[-1],
                    (WhitespaceSegment, NewlineSegment, CommentSegment),
                ):
                    trailing_non_code.insert(0, real_segments.pop())

            # Check if segment_class is a RawSegment subclass (no children)
            # vs a BaseSegment subclass (has children)
            if issubclass(segment_class, RawSegment):
                # RawSegment doesn't accept segments - just return child
                # If we have exactly one real segment, return it (with non-code siblings)
                if len(real_segments) == 1:
                    all_segments = (
                        leading_non_code + [real_segments[0]] + trailing_non_code
                    )
                    if len(all_segments) > 1:
                        # Return the segment AND the surrounding non-code segments
                        class _SegmentTuple:
                            def __init__(self, segments):
                                self.segments = tuple(segments)

                        return _SegmentTuple(all_segments)
                    return real_segments[0]
                # Otherwise, fall through to the normal handling
                # This shouldn't happen for RawSegment types, but handle gracefully

            # Calculate position marker from children
            pos_marker = None
            if real_segments and all(seg.pos_marker for seg in real_segments):
                from sqlfluff.core.parser.markers import PositionMarker

                pos_marker = PositionMarker.from_child_markers(
                    [seg.pos_marker for seg in real_segments]
                )
            segment = segment_class(
                segments=tuple(real_segments),
                pos_marker=pos_marker,
            )

            # Return segment with leading/trailing non-code segments as siblings
            all_segments = leading_non_code + [segment] + trailing_non_code
            if len(all_segments) > 1:

                class _SegmentTuple:
                    def __init__(self, segments):
                        self.segments = tuple(segments)

                return _SegmentTuple(all_segments)
            return segment

        # segment_class is None - return children unwrapped
        # This can happen with grammar-only references
        # Filter to real segments only
        real_segments = [s for s in child_segments if isinstance(s, BaseSegment)]
        # Strip leading and trailing non-code segments, preserving them for parent
        from sqlfluff.core.parser.segments.common import (
            CommentSegment,
            NewlineSegment,
            WhitespaceSegment,
        )

        # Strip leading non-code
        leading_non_code2 = []
        while real_segments and isinstance(
            real_segments[0], (WhitespaceSegment, NewlineSegment, CommentSegment)
        ):
            leading_non_code2.append(real_segments.pop(0))

        # Strip trailing non-code
        trailing_non_code2 = []
        while real_segments and isinstance(
            real_segments[-1], (WhitespaceSegment, NewlineSegment, CommentSegment)
        ):
            trailing_non_code2.insert(0, real_segments.pop())

        # For grammar-only references (segment_class is None), return children unwrapped
        # If single child: return it directly
        # If multiple children: return as tuple for parent to flatten
        if len(real_segments) == 0:
            return None
        elif len(real_segments) == 1:
            all_segments = leading_non_code2 + [real_segments[0]] + trailing_non_code2
            if len(all_segments) > 1:

                class _SegmentTuple:
                    def __init__(self, segments):
                        self.segments = tuple(segments)

                return _SegmentTuple(all_segments)
            return real_segments[0]
        else:
            # Multiple children - return as tuple so parent can flatten them
            # Don't wrap in BaseSegment as that creates unwanted "base:" nodes
            all_segments = leading_non_code2 + real_segments + trailing_non_code2

            class _SegmentTuple:
                def __init__(self, segments):
                    self.segments = tuple(segments)

            return _SegmentTuple(all_segments)

    # Handle container nodes (Sequence, DelimitedList, Bracketed)
    if node_type in ("sequence", "delimited_list", "bracketed"):
        children_nodes = node.children()
        if children_nodes is None or len(children_nodes) == 0:
            return None

        # Convert all children
        children_segments = [
            rsnode_to_segment(child, tokens, config, tf) for child in children_nodes
        ]
        children_segments = [s for s in children_segments if s is not None]

        if not children_segments:
            return None

        # Flatten any _SegmentTuple markers from nested sequences
        flattened = []
        for seg in children_segments:
            if (
                hasattr(seg, "segments")
                and hasattr(seg, "__class__")
                and seg.__class__.__name__ == "_SegmentTuple"
            ):
                flattened.extend(seg.segments)
            else:
                flattened.append(seg)
        children_segments = flattened

        # For container nodes, we should NOT wrap them in BaseSegment.
        # Instead, return a special marker that tells the parent Ref node
        # to use these children directly.
        # If there's only one child, return it unwrapped.
        if len(children_segments) == 1:
            return children_segments[0]

        # If multiple children, we need to return them somehow.
        # The problem is that a Ref node expects a single child.
        # The solution: create a tuple marker segment that the Ref handler can detect
        class _SegmentTuple:
            """Temporary marker for multiple segments that should be flattened."""

            def __init__(self, segments):
                self.segments = tuple(segments)

        return _SegmentTuple(children_segments)

    # Handle meta nodes (indent, dedent, etc.)
    if node_type == "meta":
        # Meta nodes don't produce segments in the tree
        return None

    raise ValueError(f"Unknown node type: {node_type}")


def _get_segment_class_for_token(
    token_type: str, _config: "FluffConfig"
) -> type[RawSegment]:
    """Get the appropriate RawSegment class for a token type.

    Most tokens are just RawSegment, but some have specialized classes.
    """
    from sqlfluff.core.parser.segments import (
        CodeSegment,
        CommentSegment,
        IdentifierSegment,
        KeywordSegment,
        LiteralSegment,
        NewlineSegment,
        SymbolSegment,
        WhitespaceSegment,
    )

    # Map token types to segment classes
    segment_map = {
        "whitespace": WhitespaceSegment,
        "newline": NewlineSegment,
        "comment": CommentSegment,
        "keyword": KeywordSegment,
        "identifier": IdentifierSegment,
        "literal": LiteralSegment,
        "numeric_literal": LiteralSegment,
        "string_literal": LiteralSegment,
        "symbol": SymbolSegment,
        "code": CodeSegment,
    }

    return segment_map.get(token_type.lower(), RawSegment)


def _get_segment_class(segment_type: str, config: "FluffConfig") -> type[BaseSegment]:
    """Get a segment class by name from the dialect.

    Args:
        segment_type: The segment type name (e.g., "select_statement" or "SelectStatementSegment")
        config: The FluffConfig (provides access to dialect)

    Returns:
        The segment class
    """
    # Convert snake_case to PascalCase if needed
    if not segment_type.endswith("Segment"):
        # Snake case: column_reference → ColumnReferenceSegment
        # Single word: statement → StatementSegment, file → FileSegment
        if "_" in segment_type:
            segment_type = (
                "".join(word.capitalize() for word in segment_type.split("_"))
                + "Segment"
            )
        else:
            segment_type = segment_type.capitalize() + "Segment"

    dialect = config.get("dialect_obj")
    return dialect.get_segment(segment_type)


def _is_valid_segment_class(segment_name: str, config: "FluffConfig") -> bool:
    """Check if a name refers to a valid segment class in the dialect.

    This is the authoritative check - it queries the dialect's _library to determine
    if the name refers to an actual segment class (vs a grammar element).

    Args:
        segment_name: The name to check (e.g., "AsAliasOperatorSegment", "base", "SelectableGrammar")
        config: The FluffConfig (provides access to dialect)

    Returns:
        True if the name is a valid segment class, False otherwise (grammar or not found)
    """
    # Grammar names (e.g., "SelectableGrammar") aren't segment classes
    if segment_name.endswith("Grammar"):
        return False

    dialect = config.get("dialect_obj")
    item = dialect._library.get(segment_name)

    # Must be a type (class) and a BaseSegment subclass
    return item is not None and isinstance(item, type) and issubclass(item, BaseSegment)


def _get_segment_class_by_name(
    segment_name: str, config: "FluffConfig"
) -> type[BaseSegment]:
    """Get a segment class by its exact class name from the dialect.

    Args:
        segment_name: The segment CLASS name (e.g., "AsAliasOperatorSegment")
        config: The FluffConfig (provides access to dialect)

    Returns:
        The segment class

    Raises:
        ValueError: If the segment class is not found in the dialect,
                    or if the name refers to a grammar instead of a segment class
    """
    if not _is_valid_segment_class(segment_name, config):
        if segment_name.endswith("Grammar"):
            raise ValueError(f"'{segment_name}' is a grammar, not a segment class")

        dialect = config.get("dialect_obj")
        item = dialect._library.get(segment_name)

        if item is None:
            raise ValueError(f"Segment '{segment_name}' not found in dialect")

        raise ValueError(
            f"'{segment_name}' is not a segment class (got {type(item).__name__})"
        )

    dialect = config.get("dialect_obj")
    return dialect.get_segment(segment_name)
