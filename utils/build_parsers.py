"""For autogenerating rust parsers."""

import argparse
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from sqlfluff.core.dialects import dialect_selector
from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.parser.grammar.anyof import (
    AnyNumberOf,
    AnySetOf,
    OneOf,
    OptionallyBracketed,
)
from sqlfluff.core.parser.grammar.base import Anything, Nothing, Ref
from sqlfluff.core.parser.grammar.conditional import Conditional
from sqlfluff.core.parser.grammar.delimited import Delimited, OptionallyDelimited
from sqlfluff.core.parser.grammar.sequence import Bracketed, Sequence
from sqlfluff.core.parser.parsers import (
    MultiStringParser,
    RegexParser,
    StringParser,
    TypedParser,
)
from sqlfluff.core.parser.segments.base import BaseSegment, SegmentMetaclass
from sqlfluff.core.parser.segments.meta import MetaSegment


@dataclass
class DummyParseContext:
    """Dummy context for parse context."""

    dialect: Dialect
    uuid: int


@dataclass
class GrammarInstData:
    """Data for a single GrammarInst (before serialization to Rust)."""

    variant: str
    flags: int
    parse_mode: str
    first_child_idx: int
    child_count: int
    min_times: int
    first_terminator_idx: int
    terminator_count: int
    aux_data_offset: int
    simple_hint_idx: int
    comment: str = ""


@dataclass
class SimpleHintData:
    """Data for a simple hint (indices into hint_string_indices table)."""

    raw_values_start: int  # Start index into hint_string_indices
    raw_values_count: int  # Number of raw value indices
    token_types_start: int  # Start index into hint_string_indices
    token_types_count: int  # Number of token type indices


class TableBuilder:
    """Flattens Python Grammar AST into flat table representation."""

    # GrammarFlags bit positions
    # (must match sqlfluffrs_types::grammar_inst::GrammarFlags)
    FLAG_OPTIONAL = 1 << 0
    FLAG_RESET_TERMINATORS = 1 << 1
    FLAG_ALLOW_GAPS = 1 << 2
    FLAG_ALLOW_TRAILING = 1 << 3
    FLAG_OPTIONAL_DELIMITER = 1 << 4
    FLAG_HAS_SIMPLE_HINT = 1 << 5
    FLAG_HAS_EXCLUDE = 1 << 6
    FLAG_IS_CONDITIONAL = 1 << 8  # For Meta - whether it's a Conditional Meta

    def __init__(self):
        # Core tables
        self.instructions: List[GrammarInstData] = []
        self.child_ids: List[int] = []
        self.terminators: List[int] = []
        self.strings: List[str] = []
        self.aux_data: List[int] = []
        self.regex_patterns: List[str] = []
        self.simple_hints: List[SimpleHintData] = []
        self.hint_string_indices: List[int] = []  # Indices into strings for hints
        # Per-instruction segment type index (into strings) or 0xFFFFFFFF
        # if none
        self.segment_type_offsets: List[int] = []
        # Per-instruction segment class name index (into strings) or
        # 0xFFFFFFFF if none
        self.segment_class_offsets: List[int] = []
        # Per-instruction casefold mode (0=None, 1=Upper, 2=Lower) or 0xFF
        # if unspecified
        self.casefold_offsets: List[int] = []
        # Per-instruction trim_chars: offset into trim_chars_data
        # (0xFFFFFFFF if none)
        self.trim_chars_offsets: List[int] = []
        # Per-instruction trim_chars count
        self.trim_chars_counts: List[int] = []
        # Flat array of string indices for trim_chars values
        self.trim_chars_data: List[int] = []

        # Deduplication maps
        self.string_to_id: Dict[str, int] = {}
        self.regex_to_id: Dict[str, int] = {}
        self.grammar_to_id: Dict[int, int] = {}  # Python id() -> GrammarId

        # Keep references to synthetic grammars to prevent garbage collection.
        # Python may reuse memory addresses for new objects after GC, which
        # would cause incorrect cache hits in grammar_to_id when using id().
        self._synthetic_grammars: List = []
        self.hint_to_id: Dict[Tuple[Tuple[str, ...], Tuple[str, ...]], int] = {}

    def _add_string(self, s: str) -> int:
        """Add string to table (deduplicated). Returns string_id."""
        if s in self.string_to_id:
            return self.string_to_id[s]
        string_id = len(self.strings)
        self.strings.append(s)
        self.string_to_id[s] = string_id
        return string_id

    def _add_regex(self, pattern: str) -> int:
        """Add regex pattern to table (deduplicated). Returns regex_id."""
        if pattern in self.regex_to_id:
            return self.regex_to_id[pattern]
        regex_id = len(self.regex_patterns)
        self.regex_patterns.append(pattern)
        self.regex_to_id[pattern] = regex_id
        return regex_id

    def _add_simple_hint(self, grammar, parse_context) -> int:
        """Precompute and add simple hint. Returns hint_id (0 = None)."""
        try:
            hint = grammar.simple(parse_context)
            if hint is None:
                return 0  # 0 means no hint

            # Create hashable key for deduplication
            raw_tuple = tuple(sorted(hint[0]))
            types_tuple = tuple(sorted(hint[1]))
            key = (raw_tuple, types_tuple)

            if key in self.hint_to_id:
                return self.hint_to_id[key]

            # Store raw values in strings table (reusing existing deduplication)
            raw_indices = [self._add_string(raw) for raw in raw_tuple]
            type_indices = [self._add_string(typ) for typ in types_tuple]

            # Record positions in hint_string_indices array
            raw_values_start = len(self.hint_string_indices)
            for idx in raw_indices:
                self.hint_string_indices.append(idx)
            raw_values_count = len(raw_indices)

            token_types_start = len(self.hint_string_indices)
            for idx in type_indices:
                self.hint_string_indices.append(idx)
            token_types_count = len(type_indices)

            # Add new hint (index 0 reserved for None)
            hint_id = len(self.simple_hints) + 1
            self.simple_hints.append(
                SimpleHintData(
                    raw_values_start=raw_values_start,
                    raw_values_count=raw_values_count,
                    token_types_start=token_types_start,
                    token_types_count=token_types_count,
                )
            )
            self.hint_to_id[key] = hint_id
            return hint_id
        except (RuntimeError, AttributeError):
            return 0  # No hint available

    def _flatten_optional(self, grammar, parse_context) -> Optional[int]:
        """Flatten optional grammar (e.g., exclude). Returns GrammarId or None."""
        if grammar is None:
            return None
        return self.flatten_grammar(grammar, parse_context)

    def _flatten_list(self, grammars: List, parse_context) -> List[int]:
        """Flatten list of grammars. Returns list of GrammarIds."""
        result = []
        for i, g in enumerate(grammars):
            child_id = self.flatten_grammar(g, parse_context)
            result.append(child_id)
        return result

    def _build_flags(self, grammar) -> int:
        """Build flags bitfield from grammar attributes."""
        flags = 0
        if hasattr(grammar, "is_optional") and grammar.is_optional():
            flags |= self.FLAG_OPTIONAL
        if hasattr(grammar, "reset_terminators") and grammar.reset_terminators:
            flags |= self.FLAG_RESET_TERMINATORS
        if hasattr(grammar, "allow_gaps") and grammar.allow_gaps:
            flags |= self.FLAG_ALLOW_GAPS
        if hasattr(grammar, "allow_trailing") and grammar.allow_trailing:
            flags |= self.FLAG_ALLOW_TRAILING
        if hasattr(grammar, "optional_delimiter") and grammar.optional_delimiter:
            flags |= self.FLAG_OPTIONAL_DELIMITER
        if getattr(grammar, "exclude", None) is not None:
            flags |= self.FLAG_HAS_EXCLUDE
        return flags

    def _get_parse_mode(self, grammar) -> str:
        """Extract ParseMode from grammar."""
        if not hasattr(grammar, "parse_mode"):
            return "Strict"
        mode_name = grammar.parse_mode.name
        if mode_name == "STRICT":
            return "Strict"
        elif mode_name == "GREEDY":
            return "Greedy"
        elif mode_name == "GREEDY_ONCE_STARTED":
            return "GreedyOnceStarted"
        return "Strict"

    def flatten_grammar(self, grammar, parse_context) -> int:
        """Recursively flatten Grammar tree to tables.

        Returns GrammarId for this node.
        """
        # Check cache
        python_id = id(grammar)
        if python_id in self.grammar_to_id:
            cached_result = self.grammar_to_id[python_id]
            return cached_result

        # Allocate new GrammarId and reserve slot
        # CRITICAL: We must append a placeholder BEFORE processing children,
        # because _convert_to_inst() recursively flattens children which will
        # append their instructions. If we don't reserve the slot first, this
        # instruction will end up at the wrong index!
        grammar_id = len(self.instructions)
        self.grammar_to_id[python_id] = grammar_id
        self.instructions.append(None)  # Reserve slot - will be replaced below
        # Reserve a slot for the segment_type offset (default: no type)
        self.segment_type_offsets.append(0xFFFFFFFF)
        # Reserve a slot for the segment_class offset (default: no class)
        self.segment_class_offsets.append(0xFFFFFFFF)
        # Reserve a slot for casefold mode (default: unspecified = 0xFF)
        self.casefold_offsets.append(0xFF)
        # Reserve slots for trim_chars (default: no trim_chars)
        self.trim_chars_offsets.append(0xFFFFFFFF)
        self.trim_chars_counts.append(0)

        # Convert to GrammarInst (variant-specific logic)
        inst_data = self._convert_to_inst(grammar, parse_context)

        # Replace the placeholder with the actual instruction
        self.instructions[grammar_id] = inst_data

        # If this grammar is a Segment class, record its `type` string index
        # into the per-instruction segment_type_offsets table. We store the
        # index into the existing strings table so runtime can map back to
        # the textual type (e.g., "keyword", "file", etc.). Use 0xFFFFFFFF
        # to indicate "no type".
        try:
            # If this grammar is a Segment class itself, use its `type` and
            # `__name__` attrs
            if isinstance(grammar, type) and issubclass(grammar, BaseSegment):
                seg_type = getattr(grammar, "type", None)
                if seg_type:
                    type_id = self._add_string(seg_type)
                    self.segment_type_offsets[grammar_id] = type_id
                # Also store the class name
                class_name = grammar.__name__
                class_id = self._add_string(class_name)
                self.segment_class_offsets[grammar_id] = class_id
            # If this grammar is a Ref to a named segment, attempt to resolve
            # the referenced name to a Segment class in the dialect library
            # and use that class's `type` and `__name__` attributes. This covers
            # the case where the generator special-circuits Segment classes by
            # flattening their `match_grammar` instead of emitting a forwarding
            # Ref instruction for the class itself.
            elif grammar.__class__ is Ref and isinstance(grammar, Ref):
                try:
                    ref_name = grammar._ref.replace(" ", "_")
                    # parse_context.dialect._library maps segment class names
                    # (with underscores) to class/type objects or grammars.
                    lib_entry = getattr(parse_context, "dialect", None)
                    if lib_entry is not None:
                        target = parse_context.dialect._library.get(ref_name)
                        if isinstance(target, type) and issubclass(target, BaseSegment):
                            seg_type = getattr(target, "type", None)
                            if seg_type:
                                type_id = self._add_string(seg_type)
                                self.segment_type_offsets[grammar_id] = type_id
                            # Also store the class name
                            class_name = target.__name__
                            class_id = self._add_string(class_name)
                            self.segment_class_offsets[grammar_id] = class_id
                except Exception:
                    # Be conservative: if lookup fails, leave as NONE
                    pass
            # If this grammar is Conditional, use its _meta type and class
            # for segment_type_offset
            elif grammar.__class__ is Conditional:
                meta_type = getattr(grammar, "_meta", None)
                if meta_type:
                    seg_type = getattr(meta_type, "type", None)
                    if seg_type:
                        type_id = self._add_string(seg_type)
                        self.segment_type_offsets[grammar_id] = type_id
                    # Also store the class name if it's a segment class
                    if isinstance(meta_type, type) and issubclass(
                        meta_type, BaseSegment
                    ):
                        class_name = meta_type.__name__
                        class_id = self._add_string(class_name)
                        self.segment_class_offsets[grammar_id] = class_id
                    if isinstance(meta_type, type) and issubclass(
                        meta_type, BaseSegment
                    ):
                        class_name = meta_type.__name__
                        class_id = self._add_string(class_name)
                        self.segment_class_offsets[grammar_id] = class_id
        except Exception:
            # Be conservative: if any introspection fails, leave as NONE
            pass

        return grammar_id

    def _convert_to_inst(self, grammar, parse_context) -> GrammarInstData:
        """Convert single Grammar node to GrammarInst fields."""
        # Ref
        if grammar.__class__ is Ref and isinstance(grammar, Ref):
            return self._handle_ref(grammar, parse_context)

        # Sequence
        elif grammar.__class__ is Sequence and isinstance(grammar, Sequence):
            return self._handle_sequence(grammar, parse_context)

        # OneOf (and OptionallyBracketed)
        elif (
            grammar.__class__ is OneOf or grammar.__class__ is OptionallyBracketed
        ) and isinstance(grammar, OneOf):
            return self._handle_oneof(grammar, parse_context)

        # AnyNumberOf
        elif grammar.__class__ is AnyNumberOf and isinstance(grammar, AnyNumberOf):
            return self._handle_anynumberof(grammar, parse_context)

        # AnySetOf
        elif grammar.__class__ is AnySetOf and isinstance(grammar, AnySetOf):
            return self._handle_anysetof(grammar, parse_context)

        # Delimited (and OptionallyDelimited)
        elif grammar.__class__ in (Delimited, OptionallyDelimited) and isinstance(
            grammar, Delimited
        ):
            return self._handle_delimited(grammar, parse_context)

        # Bracketed
        elif grammar.__class__ is Bracketed and isinstance(grammar, Bracketed):
            return self._handle_bracketed(grammar, parse_context)

        # StringParser
        elif grammar.__class__ is StringParser and isinstance(grammar, StringParser):
            return self._handle_string_parser(grammar, parse_context)

        # TypedParser
        elif grammar.__class__ is TypedParser and isinstance(grammar, TypedParser):
            return self._handle_typed_parser(grammar, parse_context)

        # MultiStringParser
        elif grammar.__class__ is MultiStringParser and isinstance(
            grammar, MultiStringParser
        ):
            return self._handle_multistring_parser(grammar, parse_context)

        # RegexParser
        elif grammar.__class__ is RegexParser and isinstance(grammar, RegexParser):
            return self._handle_regex_parser(grammar, parse_context)

        # Nothing
        elif grammar.__class__ is Nothing:
            return self._handle_nothing(grammar, parse_context)

        # Anything
        elif isinstance(grammar, Anything):
            return self._handle_anything(grammar, parse_context)

        # Conditional
        elif grammar.__class__ is Conditional:
            return self._handle_conditional(grammar, parse_context)

        # MetaSegment
        elif issubclass(grammar, MetaSegment):
            return self._handle_meta(grammar, parse_context)

        # SegmentMetaclass with match_grammar
        elif (
            grammar.__class__ is SegmentMetaclass
            and isinstance(grammar, SegmentMetaclass)
            and hasattr(grammar, "match_grammar")
        ):
            # Recurse into match_grammar to ensure it's flattened into the tables
            self.flatten_grammar(grammar.match_grammar, parse_context)

            # Return a forwarding instruction (use Ref variant)
            comment = f"Forward to {grammar.__name__}"
            name_id = self._add_string(grammar.__name__)
            return GrammarInstData(
                variant="Ref",
                flags=0,
                parse_mode="Strict",
                first_child_idx=len(self.child_ids),
                child_count=0,
                min_times=0,
                first_terminator_idx=len(self.terminators),
                terminator_count=0,
                aux_data_offset=name_id,
                simple_hint_idx=0,
                comment=comment,
            )

        # BaseSegment without match_grammar (Token)
        elif issubclass(grammar, BaseSegment) and not hasattr(grammar, "match_grammar"):
            return self._handle_token(grammar, parse_context)

        # Fallback: Missing
        else:
            return self._handle_missing(grammar, parse_context)

    def _handle_ref(self, grammar: Ref, parse_context) -> GrammarInstData:
        """Convert Ref to GrammarInst."""
        name_id = self._add_string(grammar._ref.replace(" ", "_"))
        flags = self._build_flags(grammar)
        hint_id = self._add_simple_hint(grammar, parse_context)

        # Flatten exclude (optional child)
        # CRITICAL: Reserve slots BEFORE flattening children, because
        # _flatten_optional/_flatten_list recursively processes child grammars
        # which may themselves add to child_ids. Reserving prevents children
        # being appended at the wrong index.
        children_start = len(self.child_ids)
        num_children = 1 if getattr(grammar, "exclude", None) is not None else 0
        if num_children:
            self.child_ids.extend([0] * num_children)

        exclude_id = self._flatten_optional(grammar.exclude, parse_context)
        if exclude_id is not None:
            # Place the exclude_id into the reserved slot
            self.child_ids[children_start] = exclude_id
        children_count = num_children

        # Flatten terminators
        terminators_start = len(self.terminators)
        terminator_ids = self._flatten_list(grammar.terminators, parse_context)
        self.terminators.extend(terminator_ids)
        terminators_count = len(terminator_ids)

        comment = f"Ref({grammar._ref})"

        return GrammarInstData(
            variant="Ref",
            flags=flags,
            parse_mode="Strict",
            first_child_idx=children_start,
            child_count=children_count,
            min_times=0,
            first_terminator_idx=terminators_start,
            terminator_count=terminators_count,
            aux_data_offset=name_id,
            simple_hint_idx=hint_id,
            comment=comment,
        )

    def _handle_sequence(self, grammar: Sequence, parse_context) -> GrammarInstData:
        """Convert Sequence to GrammarInst."""
        flags = self._build_flags(grammar)
        parse_mode = self._get_parse_mode(grammar)
        hint_id = self._add_simple_hint(grammar, parse_context)

        # Flatten elements
        # CRITICAL: Reserve slots BEFORE flattening children, because _flatten_list
        # recursively processes child grammars which may themselves add to child_ids!
        # If we don't reserve first, children_start becomes stale.
        children_start = len(self.child_ids)

        # First pass: just count how many children we'll have
        num_children = len(grammar._elements)
        # Reserve slots with placeholders
        self.child_ids.extend([0] * num_children)

        # Now flatten children - they may append MORE child_ids, but our slots are safe
        element_ids = self._flatten_list(grammar._elements, parse_context)

        # Replace the placeholders with actual IDs
        for i, eid in enumerate(element_ids):
            self.child_ids[children_start + i] = eid

        children_count = len(element_ids)

        # Flatten terminators
        terminators_start = len(self.terminators)
        terminator_ids = self._flatten_list(grammar.terminators, parse_context)
        self.terminators.extend(terminator_ids)
        terminators_count = len(terminator_ids)

        comment = f"Sequence({children_count} elements)"

        return GrammarInstData(
            variant="Sequence",
            flags=flags,
            parse_mode=parse_mode,
            first_child_idx=children_start,
            child_count=children_count,
            min_times=0,
            first_terminator_idx=terminators_start,
            terminator_count=terminators_count,
            aux_data_offset=0,
            simple_hint_idx=hint_id,
            comment=comment,
        )

    def _handle_oneof(self, grammar: OneOf, parse_context) -> GrammarInstData:
        """Convert OneOf to GrammarInst."""
        flags = self._build_flags(grammar)
        parse_mode = self._get_parse_mode(grammar)
        hint_id = self._add_simple_hint(grammar, parse_context)
        # Flatten elements + exclude
        # CRITICAL: Reserve slots BEFORE flattening children, because _flatten_list
        # recursively processes child grammars which may themselves add to child_ids!
        # If we don't reserve first, children_start becomes stale and the
        # resulting first_child_idx will point at the wrong slice.
        children_start = len(self.child_ids)
        num_children = len(grammar._elements)
        has_exclude = grammar.exclude is not None
        # Reserve placeholder slots - include one extra slot for exclude if present
        slots_to_reserve = num_children + (1 if has_exclude else 0)
        self.child_ids.extend([0] * slots_to_reserve)

        # Now flatten children - they may append MORE child_ids, but our slots are safe
        element_ids = self._flatten_list(grammar._elements, parse_context)

        # Replace the placeholders with actual IDs
        for i, eid in enumerate(element_ids):
            self.child_ids[children_start + i] = eid

        exclude_id = self._flatten_optional(grammar.exclude, parse_context)
        if exclude_id is not None:
            # Place exclude in its reserved slot (last slot)
            self.child_ids[children_start + len(element_ids)] = exclude_id

        children_count = len(element_ids) + (1 if exclude_id is not None else 0)

        # Store exclude marker in aux_data (1 if has exclude, 0 otherwise)
        aux_offset = len(self.aux_data)
        self.aux_data.append(1 if exclude_id is not None else 0)

        # Flatten terminators
        terminators_start = len(self.terminators)
        terminator_ids = self._flatten_list(grammar.terminators, parse_context)
        self.terminators.extend(terminator_ids)
        terminators_count = len(terminator_ids)

        comment = f"OneOf({len(element_ids)} options)"

        return GrammarInstData(
            variant="OneOf",
            flags=flags,
            parse_mode=parse_mode,
            first_child_idx=children_start,
            child_count=children_count,
            min_times=0,
            first_terminator_idx=terminators_start,
            terminator_count=terminators_count,
            aux_data_offset=aux_offset,
            simple_hint_idx=hint_id,
            comment=comment,
        )

    def _handle_anynumberof(
        self, grammar: AnyNumberOf, parse_context
    ) -> GrammarInstData:
        """Convert AnyNumberOf to GrammarInst."""
        flags = self._build_flags(grammar)
        parse_mode = self._get_parse_mode(grammar)
        hint_id = self._add_simple_hint(grammar, parse_context)

        # Flatten elements + exclude
        # Reserve placeholder slots BEFORE flattening so recursive flattening
        # doesn't shift our target slice.
        children_start = len(self.child_ids)
        num_children = len(grammar._elements) + (
            1 if getattr(grammar, "exclude", None) is not None else 0
        )
        if num_children:
            self.child_ids.extend([0] * num_children)

        element_ids = self._flatten_list(grammar._elements, parse_context)
        # Write back element ids into reserved slots
        for i, eid in enumerate(element_ids):
            self.child_ids[children_start + i] = eid

        exclude_id = self._flatten_optional(grammar.exclude, parse_context)
        if exclude_id is not None:
            # Place exclude in the reserved slot after elements
            self.child_ids[children_start + len(element_ids)] = exclude_id

        children_count = len(element_ids) + (1 if exclude_id is not None else 0)

        # Store min/max/max_per_element in aux_data
        aux_offset = len(self.aux_data)
        self.aux_data.append(grammar.min_times)
        self.aux_data.append(
            grammar.max_times if grammar.max_times is not None else 0xFFFFFFFF
        )
        self.aux_data.append(
            grammar.max_times_per_element
            if grammar.max_times_per_element is not None
            else 0xFFFFFFFF
        )
        self.aux_data.append(1 if exclude_id is not None else 0)

        # Flatten terminators
        terminators_start = len(self.terminators)
        terminator_ids = self._flatten_list(grammar.terminators, parse_context)
        self.terminators.extend(terminator_ids)
        terminators_count = len(terminator_ids)

        comment = f"AnyNumberOf({len(element_ids)} elements, min={grammar.min_times})"

        return GrammarInstData(
            variant="AnyNumberOf",
            flags=flags,
            parse_mode=parse_mode,
            first_child_idx=children_start,
            child_count=children_count,
            min_times=grammar.min_times,
            first_terminator_idx=terminators_start,
            terminator_count=terminators_count,
            aux_data_offset=aux_offset,
            simple_hint_idx=hint_id,
            comment=comment,
        )

    def _handle_anysetof(self, grammar: AnySetOf, parse_context) -> GrammarInstData:
        """Convert AnySetOf to GrammarInst.

        - Same as AnyNumberOf but max_times_per_element=1
        """
        flags = self._build_flags(grammar)
        parse_mode = self._get_parse_mode(grammar)
        hint_id = self._add_simple_hint(grammar, parse_context)

        # Flatten elements + exclude
        children_start = len(self.child_ids)
        num_children = len(grammar._elements) + (
            1 if getattr(grammar, "exclude", None) is not None else 0
        )
        if num_children:
            self.child_ids.extend([0] * num_children)

        element_ids = self._flatten_list(grammar._elements, parse_context)
        for i, eid in enumerate(element_ids):
            self.child_ids[children_start + i] = eid

        exclude_id = self._flatten_optional(grammar.exclude, parse_context)
        if exclude_id is not None:
            self.child_ids[children_start + len(element_ids)] = exclude_id

        children_count = len(element_ids) + (1 if exclude_id is not None else 0)

        # Store min/max in aux_data with max_per_element=1 for AnySetOf
        # This matches the 4-entry format expected by anynumberof_config:
        # [min_times, max_times, max_times_per_element, has_exclude]
        aux_offset = len(self.aux_data)
        self.aux_data.append(grammar.min_times)
        self.aux_data.append(
            grammar.max_times if grammar.max_times is not None else 0xFFFFFFFF
        )
        self.aux_data.append(1)  # max_times_per_element=1 for AnySetOf
        self.aux_data.append(1 if exclude_id is not None else 0)  # has_exclude

        # Flatten terminators
        terminators_start = len(self.terminators)
        terminator_ids = self._flatten_list(grammar.terminators, parse_context)
        self.terminators.extend(terminator_ids)
        terminators_count = len(terminator_ids)

        comment = f"AnySetOf({len(element_ids)} elements)"

        return GrammarInstData(
            # Delegated to AnyNumberOf to reduce required logic
            variant="AnyNumberOf",
            flags=flags,
            parse_mode=parse_mode,
            first_child_idx=children_start,
            child_count=children_count,
            min_times=grammar.min_times,
            first_terminator_idx=terminators_start,
            terminator_count=terminators_count,
            aux_data_offset=aux_offset,
            simple_hint_idx=hint_id,
            comment=comment,
        )

    def _handle_delimited(self, grammar: Delimited, parse_context) -> GrammarInstData:
        """Convert Delimited to GrammarInst.

        When there are multiple elements, wraps them in a OneOf to match
        Python's behavior where Delimited inherits from OneOf.
        Structure:
        - Child 0: OneOf(elements) if multiple elements, or single element
        - Child 1: delimiter
        """
        flags = self._build_flags(grammar)
        parse_mode = self._get_parse_mode(grammar)
        hint_id = self._add_simple_hint(grammar, parse_context)

        # Flatten elements + delimiter
        # Structure: [elements_oneof_or_single, delimiter]
        children_start = len(self.child_ids)
        # Always 2 children: elements (wrapped in OneOf if >1) + delimiter
        num_children = 2
        self.child_ids.extend([0] * num_children)

        # If multiple elements, wrap them in a OneOf
        # This matches Python's Delimited which inherits from OneOf
        if len(grammar._elements) > 1:
            # Create a synthetic OneOf for the elements
            # Use the same allow_gaps and parse_mode as the Delimited
            elements_oneof = OneOf(
                *grammar._elements,
                allow_gaps=grammar.allow_gaps,
                optional=True,  # Elements in Delimited are implicitly optional
            )
            # Keep reference to prevent GC and id() reuse
            self._synthetic_grammars.append(elements_oneof)
            elements_id = self.flatten_grammar(elements_oneof, parse_context)
            comment = f"Delimited({len(grammar._elements)} elements via OneOf)"
        else:
            # Single element - add it directly
            elements_id = self.flatten_grammar(grammar._elements[0], parse_context)
            comment = "Delimited(1 element)"

        self.child_ids[children_start] = elements_id

        # Add delimiter as second child
        delimiter_id = self.flatten_grammar(grammar.delimiter, parse_context)
        self.child_ids[children_start + 1] = delimiter_id

        children_count = 2

        # Store delimiter index (always 1 now) + min_delimiters in aux_data
        aux_offset = len(self.aux_data)
        self.aux_data.append(1)  # delimiter_child_index (always child 1)
        self.aux_data.append(grammar.min_delimiters)

        # Flatten terminators
        terminators_start = len(self.terminators)
        terminator_ids = self._flatten_list(grammar.terminators, parse_context)
        self.terminators.extend(terminator_ids)
        terminators_count = len(terminator_ids)

        return GrammarInstData(
            variant="Delimited",
            flags=flags,
            parse_mode=parse_mode,
            first_child_idx=children_start,
            child_count=children_count,
            min_times=grammar.min_delimiters,
            first_terminator_idx=terminators_start,
            terminator_count=terminators_count,
            aux_data_offset=aux_offset,
            simple_hint_idx=hint_id,
            comment=comment,
        )

    def _handle_bracketed(self, grammar: Bracketed, parse_context) -> GrammarInstData:
        """Convert Bracketed to GrammarInst."""
        flags = self._build_flags(grammar)
        parse_mode = self._get_parse_mode(grammar)
        hint_id = self._add_simple_hint(grammar, parse_context)

        # Flatten elements + brackets
        children_start = len(self.child_ids)
        element_count = len(grammar._elements)

        # Reserve space for all elements + two brackets
        num_children = element_count + 2
        self.child_ids.extend([0] * num_children)

        # Flatten all content elements directly
        for i, element in enumerate(grammar._elements):
            element_id = self.flatten_grammar(element, parse_context)
            self.child_ids[children_start + i] = element_id

        # Add brackets after elements
        start_bracket, end_bracket, persists = grammar.get_bracket_from_dialect(
            parse_context
        )
        start_bracket_id = self.flatten_grammar(
            grammar.start_bracket or start_bracket, parse_context
        )
        end_bracket_id = self.flatten_grammar(
            grammar.end_bracket or end_bracket, parse_context
        )
        self.child_ids[children_start + element_count] = start_bracket_id
        self.child_ids[children_start + element_count + 1] = end_bracket_id

        children_count = element_count + 2

        # Store bracket indices and persists in aux_data
        aux_offset = len(self.aux_data)
        self.aux_data.append(element_count)  # start_bracket_index
        self.aux_data.append(element_count + 1)  # end_bracket_index
        self.aux_data.append(1 if persists else 0)  # persists flag as int

        # Flatten terminators
        terminators_start = len(self.terminators)
        terminator_ids = self._flatten_list(grammar.terminators, parse_context)
        self.terminators.extend(terminator_ids)
        terminators_count = len(terminator_ids)

        comment = (
            f"Bracketed({len(grammar._elements)} elements -> {element_count} child)"
        )

        return GrammarInstData(
            variant="Bracketed",
            flags=flags,
            parse_mode=parse_mode,
            first_child_idx=children_start,
            child_count=children_count,
            min_times=0,
            first_terminator_idx=terminators_start,
            terminator_count=terminators_count,
            aux_data_offset=aux_offset,
            simple_hint_idx=hint_id,
            comment=comment,
        )

    def _handle_string_parser(
        self, grammar: StringParser, parse_context
    ) -> GrammarInstData:
        """Convert StringParser to GrammarInst."""
        template_id = self._add_string(grammar.template)
        token_type_id = self._add_string(grammar._instance_types[0])
        raw_class_id = self._add_string(grammar.raw_class.__name__)

        flags = self._build_flags(grammar)

        # Store ids in aux_data
        aux_offset = len(self.aux_data)
        self.aux_data.append(template_id)
        self.aux_data.append(token_type_id)
        self.aux_data.append(raw_class_id)

        # Generate hint for StringParser (matches exact string)
        hint_id = self._add_simple_hint(grammar, parse_context)

        comment = f'StringParser("{grammar.template}")'

        return GrammarInstData(
            variant="StringParser",
            flags=flags,
            parse_mode="Strict",
            first_child_idx=len(self.child_ids),
            child_count=0,
            min_times=0,
            first_terminator_idx=len(self.terminators),
            terminator_count=0,
            aux_data_offset=aux_offset,
            simple_hint_idx=hint_id,
            comment=comment,
        )

    def _handle_typed_parser(
        self, grammar: TypedParser, parse_context
    ) -> GrammarInstData:
        """Convert TypedParser to GrammarInst."""
        template_id = self._add_string(grammar.template)
        token_type_id = self._add_string(grammar._instance_types[0])
        raw_class_id = self._add_string(grammar.raw_class.__name__)

        flags = self._build_flags(grammar)

        # Extract casefold and store in casefold_offsets
        grammar_id = len(self.instructions) - 1  # Current grammar being built
        casefold_attr = getattr(grammar, "casefold", None)
        if casefold_attr is str.upper:
            self.casefold_offsets[grammar_id] = 1  # Upper
        elif casefold_attr is str.lower:
            self.casefold_offsets[grammar_id] = 2  # Lower
        # else: leave as 0xFF (unspecified)

        # Extract trim_chars and store in trim_chars arrays
        trim_chars_attr = getattr(grammar, "_trim_chars", None)
        if trim_chars_attr:
            # Store offset into trim_chars_data
            self.trim_chars_offsets[grammar_id] = len(self.trim_chars_data)
            self.trim_chars_counts[grammar_id] = len(trim_chars_attr)
            # Add each trim char string to the data array
            for tc in trim_chars_attr:
                tc_id = self._add_string(tc)
                self.trim_chars_data.append(tc_id)
        # else: leave as 0xFFFFFFFF (no trim_chars)

        # Store ids in aux_data
        aux_offset = len(self.aux_data)
        self.aux_data.append(template_id)
        self.aux_data.append(token_type_id)
        self.aux_data.append(raw_class_id)

        comment = f'TypedParser("{grammar.template}")'

        # Generate hint for TypedParser (matches token type)
        hint_id = self._add_simple_hint(grammar, parse_context)

        return GrammarInstData(
            variant="TypedParser",
            flags=flags,
            parse_mode="Strict",
            first_child_idx=len(self.child_ids),
            child_count=0,
            min_times=0,
            first_terminator_idx=len(self.terminators),
            terminator_count=0,
            aux_data_offset=aux_offset,
            simple_hint_idx=hint_id,
            comment=comment,
        )

    def _handle_multistring_parser(
        self, grammar: MultiStringParser, parse_context
    ) -> GrammarInstData:
        """Convert MultiStringParser to GrammarInst."""
        # Add all templates
        templates_start = len(self.aux_data)
        for template in sorted(grammar.templates):
            template_id = self._add_string(template)
            self.aux_data.append(template_id)
        templates_count = len(grammar.templates)

        token_type_id = self._add_string(grammar._instance_types[0])
        raw_class_id = self._add_string(grammar.raw_class.__name__)

        flags = self._build_flags(grammar)

        # Store metadata in aux_data
        aux_offset = len(self.aux_data)
        self.aux_data.append(templates_start)
        self.aux_data.append(templates_count)
        self.aux_data.append(token_type_id)
        self.aux_data.append(raw_class_id)

        comment = f"MultiStringParser({templates_count} templates)"

        # Generate hint for MultiStringParser (matches any of the strings)
        hint_id = self._add_simple_hint(grammar, parse_context)

        return GrammarInstData(
            variant="MultiStringParser",
            flags=flags,
            parse_mode="Strict",
            first_child_idx=len(self.child_ids),
            child_count=0,
            min_times=0,
            first_terminator_idx=len(self.terminators),
            terminator_count=0,
            aux_data_offset=aux_offset,
            simple_hint_idx=hint_id,
            comment=comment,
        )

    def _handle_regex_parser(
        self, grammar: RegexParser, parse_context
    ) -> GrammarInstData:
        """Convert RegexParser to GrammarInst."""
        regex_id = self._add_regex(grammar.template)
        anti_regex_id = (
            self._add_regex(grammar.anti_template)
            if grammar.anti_template
            else 0xFFFFFFFF
        )
        token_type_id = self._add_string(grammar._instance_types[0])
        raw_class_id = self._add_string(grammar.raw_class.__name__)

        flags = self._build_flags(grammar)

        # Extract casefold and store in casefold_offsets
        grammar_id = len(self.instructions) - 1  # Current grammar being built
        casefold_attr = getattr(grammar, "casefold", None)
        if casefold_attr is str.upper:
            self.casefold_offsets[grammar_id] = 1  # Upper
        elif casefold_attr is str.lower:
            self.casefold_offsets[grammar_id] = 2  # Lower
        # else: leave as 0xFF (unspecified)

        # Store ids in aux_data
        aux_offset = len(self.aux_data)
        self.aux_data.append(regex_id)
        self.aux_data.append(anti_regex_id)
        self.aux_data.append(token_type_id)
        self.aux_data.append(raw_class_id)

        comment = "RegexParser"

        return GrammarInstData(
            variant="RegexParser",
            flags=flags,
            parse_mode="Strict",
            first_child_idx=len(self.child_ids),
            child_count=0,
            min_times=0,
            first_terminator_idx=len(self.terminators),
            terminator_count=0,
            aux_data_offset=aux_offset,
            simple_hint_idx=0,
            comment=comment,
        )

    def _handle_nothing(self, grammar: Nothing, parse_context) -> GrammarInstData:
        """Convert Nothing to GrammarInst."""
        return GrammarInstData(
            variant="Nothing",
            flags=0,
            parse_mode="Strict",
            first_child_idx=len(self.child_ids),
            child_count=0,
            min_times=0,
            first_terminator_idx=len(self.terminators),
            terminator_count=0,
            aux_data_offset=0,
            simple_hint_idx=0,
            comment="Nothing",
        )

    def _handle_anything(self, grammar: Anything, parse_context) -> GrammarInstData:
        """Convert Anything to GrammarInst."""
        flags = 0
        if grammar.reset_terminators:
            flags |= self.FLAG_RESET_TERMINATORS

        # Flatten terminators
        terminators_start = len(self.terminators)
        terminator_ids = self._flatten_list(grammar.terminators, parse_context)
        self.terminators.extend(terminator_ids)
        terminators_count = len(terminator_ids)

        return GrammarInstData(
            variant="Anything",
            flags=flags,
            parse_mode="Strict",
            first_child_idx=len(self.child_ids),
            child_count=0,
            min_times=0,
            first_terminator_idx=terminators_start,
            terminator_count=terminators_count,
            aux_data_offset=0,
            simple_hint_idx=0,
            comment="Anything",
        )

    def _handle_conditional(
        self, grammar: Conditional, parse_context
    ) -> GrammarInstData:
        """Convert Conditional to Meta with conditional configuration.

        Encodes conditional rules in aux_data:
        - aux_data[0]: meta_type string ID ("indent", "implicit_indent", "dedent", etc.)
        - aux_data[1]: config_key string ID ("indented_joins", etc.)
        - aux_data[2]: expected_value (1 for True, 0 for False)

        Note: Currently only supports a single config rule.
        """
        # Get the meta type ("indent", "dedent", etc.)
        # Check if this is an implicit indent
        is_implicit = getattr(grammar._meta, "is_implicit", False)
        if is_implicit and grammar._meta.type == "indent":
            # Use "implicit_indent" as the type to distinguish from regular indent
            meta_type = "implicit_indent"
        else:
            meta_type = grammar._meta.type
        meta_type_id = self._add_string(meta_type)

        # Get the config rules (currently only one is supported)
        if len(grammar._config_rules) != 1:
            raise ValueError(
                "Conditional with multiple rules not yet supported:"
                f" {grammar._config_rules}"
            )

        config_key, expected_value = next(iter(grammar._config_rules.items()))
        config_key_id = self._add_string(config_key)
        expected_value_int = 1 if expected_value else 0

        # Store in aux_data: [meta_type_id, config_key_id, expected_value]
        aux_offset = len(self.aux_data)
        self.aux_data.extend([meta_type_id, config_key_id, expected_value_int])

        return GrammarInstData(
            variant="Meta",
            flags=self.FLAG_IS_CONDITIONAL,
            parse_mode="Strict",
            first_child_idx=len(self.child_ids),
            child_count=0,
            min_times=0,
            first_terminator_idx=len(self.terminators),
            terminator_count=0,
            aux_data_offset=aux_offset,
            simple_hint_idx=0,
            comment=f"Meta(conditional: {config_key}={expected_value} -> {meta_type})",
        )

    def _handle_meta(self, grammar, parse_context) -> GrammarInstData:
        """Convert MetaSegment to Meta."""
        # Check if this is an implicit indent
        is_implicit = getattr(grammar, "is_implicit", False)
        if is_implicit and grammar.type == "indent":
            # Use "implicit_indent" as the type to distinguish from regular indent
            type_id = self._add_string("implicit_indent")
            type_name = "implicit_indent"
        else:
            type_id = self._add_string(grammar.type)
            type_name = grammar.type
        return GrammarInstData(
            variant="Meta",
            flags=0,
            parse_mode="Strict",
            first_child_idx=len(self.child_ids),
            child_count=0,
            min_times=0,
            first_terminator_idx=len(self.terminators),
            terminator_count=0,
            aux_data_offset=type_id,
            simple_hint_idx=0,
            comment=f'Meta("{type_name}")',
        )

    def _handle_token(self, grammar, parse_context) -> GrammarInstData:
        """Convert Token (BaseSegment without match_grammar) to GrammarInst."""
        type_id = self._add_string(grammar.type)
        return GrammarInstData(
            variant="Token",
            flags=0,
            parse_mode="Strict",
            first_child_idx=len(self.child_ids),
            child_count=0,
            min_times=0,
            first_terminator_idx=len(self.terminators),
            terminator_count=0,
            aux_data_offset=type_id,
            simple_hint_idx=0,
            comment=f'Token("{grammar.type}")',
        )

    def _handle_missing(self, grammar, parse_context) -> GrammarInstData:
        """Fallback for unhandled grammar types."""
        return GrammarInstData(
            variant="Missing",
            flags=0,
            parse_mode="Strict",
            first_child_idx=len(self.child_ids),
            child_count=0,
            min_times=0,
            first_terminator_idx=len(self.terminators),
            terminator_count=0,
            aux_data_offset=0,
            simple_hint_idx=0,
            comment=f"Missing({grammar.__class__.__name__})",
        )

    def validate(self):
        """Run sanity checks on generated tables."""
        errors = []

        for i, inst in enumerate(self.instructions):
            # Check children bounds
            if inst.first_child_idx + inst.child_count > len(self.child_ids):
                errors.append(f"Inst {i}: children out of bounds")

            # Check all child_ids are valid
            for j in range(
                inst.first_child_idx, inst.first_child_idx + inst.child_count
            ):
                if j >= len(self.child_ids):
                    errors.append(f"Inst {i}: child index {j} >= {len(self.child_ids)}")
                else:
                    child_id = self.child_ids[j]
                    if child_id >= len(self.instructions):
                        errors.append(
                            f"Inst {i}: invalid child_id {child_id}"
                            f" >= {len(self.instructions)}"
                        )

            # Check terminators bounds
            if inst.first_terminator_idx + inst.terminator_count > len(
                self.terminators
            ):
                errors.append(f"Inst {i}: terminators out of bounds")

            # Check all terminator_ids are valid
            for j in range(
                inst.first_terminator_idx,
                inst.first_terminator_idx + inst.terminator_count,
            ):
                if j >= len(self.terminators):
                    errors.append(
                        f"Inst {i}: terminator index {j} >= {len(self.terminators)}"
                    )
                else:
                    term_id = self.terminators[j]
                    if term_id >= len(self.instructions):
                        errors.append(
                            f"Inst {i}: invalid terminator_id {term_id}"
                            f" >= {len(self.instructions)}"
                        )

        if errors:
            print("// VALIDATION ERRORS:", file=sys.stderr)
            for err in errors:
                print(f"//   {err}", file=sys.stderr)
            raise ValueError(f"Table validation failed with {len(errors)} errors")

    def generate_rust_tables(self) -> str:
        """Generate Rust static table initialization code."""
        lines = []

        # Instructions
        lines.append("pub static INSTRUCTIONS: &[GrammarInst] = &[")
        for i, inst in enumerate(self.instructions):
            # Emit a single-line GrammarInst for more compact generated output.
            lines.append(f"    // [{i}] {inst.comment}")
            lines.append(
                (
                    "    GrammarInst { variant: GrammarVariant::%s, "
                    "parse_mode: ParseMode::%s, "
                    "flags: GrammarFlags::from_bits(%d), "
                    "first_child_idx: %d, child_count: %d, min_times: %d, "
                    "first_terminator_idx: %d, terminator_count: %d, _padding: 0 },"
                )
                % (
                    inst.variant,
                    inst.parse_mode,
                    inst.flags,
                    inst.first_child_idx,
                    inst.child_count,
                    inst.min_times,
                    inst.first_terminator_idx,
                    inst.terminator_count,
                )
            )
        lines.append("];")
        lines.append("")

        # Child IDs (compact format)
        lines.append("pub static CHILD_IDS: &[u32] = &[")
        for i in range(0, len(self.child_ids), 16):
            chunk = self.child_ids[i : i + 16]
            line = "    " + ", ".join(str(x) for x in chunk) + ","
            lines.append(line)
        lines.append("];")
        lines.append("")

        # Terminators (compact format)
        lines.append("pub static TERMINATORS: &[u32] = &[")
        for i in range(0, len(self.terminators), 16):
            chunk = self.terminators[i : i + 16]
            line = "    " + ", ".join(str(x) for x in chunk) + ","
            lines.append(line)
        lines.append("];")
        lines.append("")

        # Strings
        lines.append("pub static STRINGS: &[&str] = &[")
        for i, s in enumerate(self.strings):
            escaped = s.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'    "{escaped}", // [{i}]')
        lines.append("];")
        lines.append("")

        # Aux data (compact format)
        lines.append("pub static AUX_DATA: &[u32] = &[")
        for i in range(0, len(self.aux_data), 16):
            chunk = self.aux_data[i : i + 16]
            line = "    " + ", ".join(str(x) for x in chunk) + ","
            lines.append(line)
        lines.append("];")
        lines.append("")

        # Aux data offsets (indexed by GrammarId)
        lines.append("pub static AUX_DATA_OFFSETS: &[u32] = &[")
        for i in range(0, len(self.instructions), 16):
            chunk = [inst.aux_data_offset for inst in self.instructions[i : i + 16]]
            line = "    " + ", ".join(str(x) for x in chunk) + ","
            lines.append(line)
        lines.append("];")
        lines.append("")

        # Segment type offsets (indexed by GrammarId)
        # - index into STRINGS or 0xFFFFFFFF
        lines.append("pub static SEGMENT_TYPE_OFFSETS: &[u32] = &[")
        for i in range(0, len(self.segment_type_offsets), 16):
            chunk = self.segment_type_offsets[i : i + 16]
            line = "    " + ", ".join(str(x) for x in chunk) + ","
            lines.append(line)
        lines.append("];")
        lines.append("")

        # Segment class name offsets (indexed by GrammarId)
        # - index into STRINGS or 0xFFFFFFFF
        lines.append("pub static SEGMENT_CLASS_OFFSETS: &[u32] = &[")
        for i in range(0, len(self.segment_class_offsets), 16):
            chunk = self.segment_class_offsets[i : i + 16]
            line = "    " + ", ".join(str(x) for x in chunk) + ","
            lines.append(line)
        lines.append("];")
        lines.append("")

        # Casefold offsets (indexed by GrammarId)
        # - 0xFF=unspecified, 0=None, 1=Upper, 2=Lower
        lines.append("pub static CASEFOLD_OFFSETS: &[u8] = &[")
        for i in range(0, len(self.casefold_offsets), 32):
            chunk = self.casefold_offsets[i : i + 32]
            line = "    " + ", ".join(str(x) for x in chunk) + ","
            lines.append(line)
        lines.append("];")
        lines.append("")

        # Trim chars offsets (indexed by GrammarId)
        # - index into TRIM_CHARS_DATA or 0xFFFFFFFF
        lines.append("pub static TRIM_CHARS_OFFSETS: &[u32] = &[")
        for i in range(0, len(self.trim_chars_offsets), 16):
            chunk = self.trim_chars_offsets[i : i + 16]
            line = "    " + ", ".join(str(x) for x in chunk) + ","
            lines.append(line)
        lines.append("];")
        lines.append("")

        # Trim chars counts (indexed by GrammarId)
        lines.append("pub static TRIM_CHARS_COUNTS: &[u8] = &[")
        for i in range(0, len(self.trim_chars_counts), 32):
            chunk = self.trim_chars_counts[i : i + 32]
            line = "    " + ", ".join(str(x) for x in chunk) + ","
            lines.append(line)
        lines.append("];")
        lines.append("")

        # Trim chars data (flat array of string indices)
        lines.append("pub static TRIM_CHARS_DATA: &[u32] = &[")
        for i in range(0, len(self.trim_chars_data), 16):
            chunk = self.trim_chars_data[i : i + 16]
            line = "    " + ", ".join(str(x) for x in chunk) + ","
            lines.append(line)
        lines.append("];")
        lines.append("")

        # Regex patterns
        lines.append("pub static REGEX_PATTERNS: &[&str] = &[")
        for i, pattern in enumerate(self.regex_patterns):
            # Use raw string literals for regexes
            lines.append(f'    r#"{pattern}"#, // [{i}]')
        lines.append("];")
        lines.append("")

        # Hint string indices - indices into STRINGS table for hints
        lines.append("pub static HINT_STRING_INDICES: &[u32] = &[")
        for i, idx in enumerate(self.hint_string_indices):
            lines.append(f"    {idx}, // [{i}]")
        lines.append("];")
        lines.append("")

        # Simple hints - generate SimpleHintData with offsets into HINT_STRING_INDICES
        lines.append("pub static SIMPLE_HINTS: &[SimpleHintData] = &[")
        lines.append("    SimpleHintData::empty(), // [0] reserved for no hint")
        for i, hint in enumerate(self.simple_hints):
            lines.append(
                f"    SimpleHintData {{ "
                f"raw_values_start: {hint.raw_values_start}, "
                f"raw_values_count: {hint.raw_values_count}, "
                f"token_types_start: {hint.token_types_start}, "
                f"token_types_count: {hint.token_types_count} "
                f"}}, // [{i + 1}]"
            )
        lines.append("];")
        lines.append("")

        # Simple hint indices per instruction (indexed by GrammarId)
        lines.append("pub static SIMPLE_HINT_INDICES: &[u32] = &[")
        for i in range(0, len(self.instructions), 16):
            chunk = [inst.simple_hint_idx for inst in self.instructions[i : i + 16]]
            line = "    " + ", ".join(str(x) for x in chunk) + ","
            lines.append(line)
        lines.append("];")
        lines.append("")

        return "\n".join(lines)

    def print_statistics(self):
        """Print table statistics."""
        print("// Table Statistics:")
        print(
            f"//   Instructions:    {len(self.instructions):6} × 20 bytes "
            f"= {len(self.instructions) * 20:8} bytes"
        )
        print(
            f"//   Child IDs:       {len(self.child_ids):6} ×  4 bytes "
            f"= {len(self.child_ids) * 4:8} bytes"
        )
        print(
            f"//   Terminators:     {len(self.terminators):6} ×  4 bytes "
            f"= {len(self.terminators) * 4:8} bytes"
        )

        string_bytes = sum(len(s.encode("utf-8")) for s in self.strings)
        print(
            f"//   Strings:         {len(self.strings):6} strings      "
            f"= {string_bytes:8} bytes"
        )

        print(
            f"//   Aux Data:        {len(self.aux_data):6} ×  4 bytes "
            f"= {len(self.aux_data) * 4:8} bytes"
        )
        print(
            f"//   Aux Offsets:     {len(self.instructions):6} ×  4 bytes "
            f"= {len(self.instructions) * 4:8} bytes"
        )

        regex_bytes = sum(len(r.encode("utf-8")) for r in self.regex_patterns)
        print(
            f"//   Regex Patterns:  {len(self.regex_patterns):6} patterns     "
            f"= {regex_bytes:8} bytes"
        )

        # Hint bytes: 16 bytes per SimpleHintData (4 u32 fields) + hint_string_indices
        hint_data_bytes = len(self.simple_hints) * 16
        hint_indices_bytes = len(self.hint_string_indices) * 4
        hint_bytes = hint_data_bytes + hint_indices_bytes
        print(
            f"//   Simple Hints:    {len(self.simple_hints):6} hints        "
            f"= {hint_data_bytes:8} bytes"
        )
        print(
            f"//   Hint Indices:    {len(self.hint_string_indices):6} ×  4 bytes "
            f"= {hint_indices_bytes:8} bytes"
        )

        total = (
            len(self.instructions) * 20
            + len(self.child_ids) * 4
            + len(self.terminators) * 4
            + string_bytes
            + len(self.aux_data) * 4
            + len(self.instructions) * 4  # aux_data_offsets
            + regex_bytes
            + hint_bytes
        )
        print(f"//   TOTAL:                                    ≈ {total:8} bytes")
        print()


def matchable_to_const_name(s: str):
    """Convert a segment class name to a token name."""
    return re.sub(
        "_{2,}",
        "_",
        re.sub("([A-Z])", r"_\1", s).replace("-", "_").replace("$", "_").strip("_"),
    ).upper()


def generate_parser_table_driven(dialect: str):
    """Generate the table-driven parser for a dialect."""
    loaded_dialect = dialect_selector(dialect)
    parse_context = DummyParseContext(loaded_dialect, 0)

    # For table-driven generation, emit only the precise imports needed
    # at the top of the generated module. This keeps generated files clean and
    # avoids unused-import warnings in modes where certain symbols aren't used.
    print("use sqlfluffrs_types::{")
    print("    GrammarInst, GrammarVariant, GrammarFlags,")
    print("    ParseMode, GrammarId, GrammarTables,")
    print("    SimpleHintData, RootGrammar")
    print("};")

    # Build tables
    builder = TableBuilder()
    segment_to_id = {}
    segment_types = []

    # Phase 1: Flatten all segment grammars
    print("// Flattening grammar tree...")
    for name, match_grammar in sorted(loaded_dialect._library.items()):
        name = name.replace(" ", "_")

        # DEBUG
        if name == "SelectClauseSegment":
            print(f"// DEBUG: Processing {name}", file=sys.stderr)
            print(
                f"// DEBUG:   match_grammar type: {type(match_grammar).__name__}",
                file=sys.stderr,
            )
            print(
                "// DEBUG:   isinstance(match_grammar, type): "
                f"{isinstance(match_grammar, type)}",
                file=sys.stderr,
            )
            if isinstance(match_grammar, type):
                print(
                    "// DEBUG:   issubclass(match_grammar, BaseSegment): "
                    f"{issubclass(match_grammar, BaseSegment)}",
                    file=sys.stderr,
                )
                print(
                    "// DEBUG:   hasattr(match_grammar, 'match_grammar'): "
                    f"{hasattr(match_grammar, 'match_grammar')}",
                    file=sys.stderr,
                )

        # Flatten grammar
        # If this is a Segment class (SegmentMetaclass), the builder will
        # emit a forwarding Ref instruction for the class itself and a
        # separate instruction for the actual match_grammar. For RootGrammar
        # mappings we want the underlying grammar id (the real implementation),
        # not the forwarding Ref. Detect and handle that here.
        if (
            isinstance(match_grammar, type)
            and issubclass(match_grammar, BaseSegment)
            and hasattr(match_grammar, "match_grammar")
        ):
            # Flatten the concrete match_grammar and use its id
            root_id = builder.flatten_grammar(
                match_grammar.match_grammar, parse_context
            )
        else:
            root_id = builder.flatten_grammar(match_grammar, parse_context)

        segment_to_id[name] = root_id

        # Check if this is a Segment class (has a 'type' attribute)
        if isinstance(match_grammar, type) and issubclass(match_grammar, BaseSegment):
            segment_type = getattr(match_grammar, "type", None)
            if segment_type:
                segment_types.append((name, segment_type))

    # Validate tables
    print("// Validating tables...")
    builder.validate()
    print("// Validation passed!")
    print()

    # Print statistics
    builder.print_statistics()

    # Phase 2: Generate Rust code
    print(builder.generate_rust_tables())

    # Phase 3: Generate accessor functions
    print(
        f"pub fn get_{dialect.lower()}_segment_grammar(name: &str) "
        "-> Option<RootGrammar> {"
    )
    print("    match name {")
    for name, grammar_id in sorted(segment_to_id.items()):
        print(
            f'        "{name}" => Some(RootGrammar {{ '
            f"grammar_id: GrammarId({grammar_id}), "
            f"tables: &{dialect.upper()}_TABLES }}),"
        )
    print("        _ => None,")
    print("    }")
    print("}")
    print()

    # Generate type mapping function
    print(
        f"pub fn get_{dialect.lower()}_segment_type(name: &str) "
        "-> Option<&'static str> {"
    )
    print("    match name {")
    for name, segment_type in sorted(segment_types):
        print(f'        "{name}" => Some("{segment_type}"),')
    print("        _ => None,")
    print("    }")
    print("}")
    print()

    # Phase 4: Generate GrammarTables instance
    print(
        f"""pub static {dialect.upper()}_TABLES: GrammarTables = GrammarTables {{
    instructions: INSTRUCTIONS,
    child_ids: CHILD_IDS,
    terminators: TERMINATORS,
    strings: STRINGS,
    aux_data: AUX_DATA,
    aux_data_offsets: AUX_DATA_OFFSETS,
    regex_patterns: REGEX_PATTERNS,
    simple_hints: SIMPLE_HINTS,
    hint_string_indices: HINT_STRING_INDICES,
    simple_hint_indices: SIMPLE_HINT_INDICES,
    segment_type_offsets: SEGMENT_TYPE_OFFSETS,
    segment_class_offsets: SEGMENT_CLASS_OFFSETS,
    casefold_offsets: CASEFOLD_OFFSETS,
    trim_chars_offsets: TRIM_CHARS_OFFSETS,
    trim_chars_counts: TRIM_CHARS_COUNTS,
    trim_chars_data: TRIM_CHARS_DATA,
}};
"""
    )

    # Generate root grammar accessor
    root_name = loaded_dialect.get_root_segment().__name__
    root_id = segment_to_id.get(root_name, 0)
    print(
        f"""pub fn get_{dialect.lower()}_root_grammar_id() -> GrammarId {{
    GrammarId({root_id})
}}"""
    )

    # Emit RootGrammar constructor for table-driven dialect (named _table)
    print(
        f"""pub fn get_{dialect.lower()}_root_grammar_table() -> RootGrammar {{
    RootGrammar {{
        grammar_id: get_{dialect.lower()}_root_grammar_id(),
        tables: &{dialect.upper()}_TABLES,
    }}
}}"""
    )
    # Wrapper so callers can call get_<dialect>_root_grammar()
    print(f"pub fn get_{dialect.lower()}_root_grammar() -> RootGrammar {{")
    print(f"    get_{dialect.lower()}_root_grammar_table()")
    print("}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build generated Rust output for a dialect."
    )
    parser.add_argument(
        "dialect",
    )
    parser.add_argument(
        "--table-driven",
        action="store_true",
        help="Generate table-driven code (new format)",
    )
    args = parser.parse_args()
    print("/* This is a generated file! */")
    print("/* Generated by `utils/build_parsers.py` via `utils/rustify.py` */")
    print("/* This process can be run via tox: `tox -e generate-rs` */")
    print("#![cfg_attr(rustfmt, rustfmt_skip)]")
    print()

    generate_parser_table_driven(args.dialect)
