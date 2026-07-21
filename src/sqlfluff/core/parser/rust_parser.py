"""Python wrapper for Rust parser that returns BaseSegment trees.

This module provides RustParser, a drop-in replacement for the Python Parser
that uses the Rust implementation under the hood but returns Python BaseSegment
objects for compatibility with the linter infrastructure.

The Rust parser returns a MatchResult that describes what was matched (slices,
classes, inserts) without building the AST. Python's MatchResult.apply() then
constructs the BaseSegment tree, leveraging proven logic and avoiding
double-counting issues.
"""

import functools
import logging
import os
import time
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Optional, Union

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_result import MatchResult, _get_point_pos_at_idx
from sqlfluff.core.parser.segments import (
    BaseFileSegment,
    BaseSegment,
    Dedent,
    ImplicitIndent,
    Indent,
    TemplateSegment,
    UnparsableSegment,
)

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.dialects.base import Dialect

# Instantiate the parser logger
parser_logger = logging.getLogger("sqlfluff.parser")


# --- Sub-stage parse profiling -------------------------------------------------
# RustParser.parse() is a fast Rust core wrapped in O(nodes) Python work. To find
# out where the time actually goes (Rust parse vs. the Python re-conversion vs.
# building the BaseSegment tree vs. building the Rust arena tree (_rs_tree)),
# the four internal stages can be timed individually.
#
# This is OFF by default (zero overhead). Enable it either by setting the
# SQLFLUFF_RS_PROFILE environment variable, or by calling set_profiling(True)
# from tooling (e.g. utils/benchmark_parsing.py). When enabled, the most recent
# parse() call records per-stage wall-clock seconds into _PARSE_PROFILE, readable
# via get_parse_profile().
_PROFILE_ENABLED = bool(os.environ.get("SQLFLUFF_RS_PROFILE"))
_PARSE_PROFILE: dict[str, float] = {}


def set_profiling(enabled: bool) -> None:
    """Enable or disable per-stage parse profiling at runtime."""
    global _PROFILE_ENABLED
    _PROFILE_ENABLED = enabled


def reset_parse_profile() -> None:
    """Clear the accumulated per-stage profile.

    parse() accumulates timings (across rendered variants), so callers reset
    between top-level parses to scope the profile to a single source. The
    benchmark calls this before each timed iteration.
    """
    _PARSE_PROFILE.clear()


def get_parse_profile() -> dict[str, float]:
    """Return per-stage timings (seconds) accumulated since the last reset.

    parse() *accumulates* into this profile (summing across rendered variants,
    e.g. branching Jinja), so it reflects all parse() calls since the last
    reset_parse_profile() rather than just the final one. Only populated when
    profiling is enabled (see set_profiling / the SQLFLUFF_RS_PROFILE env var).
    Keys, in execution order:
        rust_core      - the Rust parse (parse_match_result_from_tokens)
        convert        - Python rebuild of the tree as a MatchResult
        apply          - building the BaseSegment tree (MatchResult.apply)
        apply_as_tree  - building the Rust arena tree (_rs_tree)
    """
    return dict(_PARSE_PROFILE)


# --- Native AST construction (experimental) ------------------------------------
# Today parse() rebuilds the Rust match tree as Python MatchResult objects
# (_convert_rs_match_result) and then walks that again to build the BaseSegment
# tree (MatchResult.apply) - two full traversals plus a throwaway intermediate
# tree. The "native AST" path fuses these into a single pass that instantiates
# BaseSegments directly from the RsMatchResult (_apply_rs_match_result),
# eliminating the intermediate MatchResult tree (the profiler's "convert" stage).
#
# OFF by default while we validate parity against the proven convert+apply path.
# Toggle via the SQLFLUFF_RS_NATIVE_AST env var or set_native_ast(True).
_NATIVE_AST_ENABLED = bool(os.environ.get("SQLFLUFF_RS_NATIVE_AST"))


def set_native_ast(enabled: bool) -> None:
    """Enable or disable the fused (native) BaseSegment builder at runtime."""
    global _NATIVE_AST_ENABLED
    _NATIVE_AST_ENABLED = enabled


def get_native_ast() -> bool:
    """Return whether the fused (native) BaseSegment builder is enabled."""
    return _NATIVE_AST_ENABLED


try:
    from sqlfluffrs import RsMatchResult, RsParseError, RsParser, RsToken

    _HAS_RUST_PARSER = True

    class RustParser:
        """Parser wrapper that uses Rust implementation but returns BaseSegment.

        This is designed to be a drop-in replacement for the Python Parser class,
        with the same interface but using the faster Rust parser internally.

        Example:
            >>> from sqlfluff.core.parser import RustParser
            >>> parser = RustParser(dialect="ansi")
            >>> segment = parser.parse(tokens, fname="test.sql")
        """

        def __init__(
            self,
            config: Optional["FluffConfig"] = None,
            dialect: Optional[str] = None,
        ) -> None:
            """Initialize the Rust parser with config or dialect.

            Args:
                config: FluffConfig instance (takes precedence over dialect)
                dialect: Dialect name (used if config not provided)

            Raises:
                ValueError: If both config and dialect are provided
            """
            if config and dialect:
                raise ValueError(  # pragma: no cover
                    "RustParser does not support setting both `config` and `dialect`."
                )

            # Use the provided config or create one from the dialect.
            self.config = config or FluffConfig.from_kwargs(dialect=dialect)
            self.RootSegment: type[BaseFileSegment] = self.config.get(
                "dialect_obj"
            ).get_root_segment()

            # Extract indentation config for Conditional grammar evaluation.
            # PYTHON PARITY: ParseContext.from_config coerces every value here
            # with bool(), not just ones already typed as bool - the ini
            # config layer can produce int 1 for a truthy setting like
            # `indented_joins = 1`, and filtering by isinstance(v, bool)
            # would silently drop it instead of coercing it.
            indent_config = self.config.get_section("indentation") or {}
            if indent_config:
                indent_config = {k: bool(v) for k, v in indent_config.items()}

            # Max parse depth (DoS mitigation); 0 disables the limit
            max_parse_depth = self.config.get("max_parse_depth")
            max_parse_nodes = self.config.get("max_parse_nodes")
            assert isinstance(max_parse_depth, int)
            assert isinstance(max_parse_nodes, int)
            assert max_parse_depth >= 0
            assert max_parse_nodes >= 0

            # Create the Rust parser
            self._rs_parser = RsParser(
                dialect=self.config.get("dialect"),
                indent_config=indent_config,
                max_parser_iterations=self.config.get("rust_parser_max_iterations")
                or None,
                parser_warn_threshold=self.config.get("rust_parser_warn_threshold")
                or None,
                max_parse_depth=max_parse_depth,
                max_parse_nodes=max_parse_nodes,
            )

        def parse(
            self,
            segments: tuple["BaseSegment", ...],
            fname: Optional[str] = None,
            parse_statistics: bool = False,
        ) -> Optional["BaseSegment"]:
            """Parse a series of lexed tokens using the Rust parser.

            This method now uses the MatchResult-based approach where Rust returns
            a MatchResult and Python's apply() builds the AST, avoiding double-counting.

            Args:
                segments: Tuple of RawSegment objects from the lexer
                fname: Optional filename for error reporting
                parse_statistics: Whether to log parse statistics (not yet implemented)
                tf: Optional TemplatedFile for position marker reconstruction

            Returns:
                BaseSegment tree representing the parsed SQL, or None if empty

            Note:
                The segments parameter contains RawSegment objects that were created
                from RsToken objects using RawSegment.from_rstoken(). To optimize,
                we need to extract the original RsToken objects to pass to the Rust
                parser directly.
            """
            try:
                if not segments:  # pragma: no cover
                    return None

                parse_context = ParseContext.from_config(config=self.config)
                parse_context.seed_parse_nodes(len(segments))

                # Per-stage profiling (no-op unless profiling is enabled).
                # NOTE: parse() runs once per rendered variant, so timings are
                # *accumulated* into _PARSE_PROFILE (see the publish step below)
                # rather than overwritten — branching templates (e.g. Jinja
                # `{% if %}`) parse multiple variants and we want their combined
                # cost, consistent with the linter's total parse time. Callers
                # reset between top-level parses via reset_parse_profile()
                # (the benchmark does this per timed iteration).
                _prof: Optional[dict[str, float]] = {} if _PROFILE_ENABLED else None
                _ts = 0.0

                # PYTHON PARITY: Trim non-code from start (like root_parse)
                _start_idx = 0
                for _start_idx in range(len(segments)):
                    if segments[_start_idx].is_code:
                        break

                # PYTHON PARITY: Trim non-code from end (like root_parse)
                _end_idx = len(segments)
                for _end_idx in range(len(segments), _start_idx - 1, -1):
                    if segments[_end_idx - 1].is_code:
                        break

                if _start_idx == _end_idx:
                    # No code segments - return FileSegment with just non-code
                    parse_context.increment_parse_nodes()
                    return self.RootSegment(segments=segments, fname=fname)

                # Extract the original RsToken objects from the RawSegments
                # PYTHON PARITY: Only parse the code portion (segments[_start_idx:_end_idx])
                # Just like Python's match(segments[:_end_idx], _start_idx, ...)
                tokens = self._extract_tokens_from_segments(
                    segments[_start_idx:_end_idx]
                )

                # Parse using Rust parser to get MatchResult
                # The Rust parser may raise RsParseError for certain parse errors (e.g.,
                # missing closing brackets in terminators). We catch these and convert to
                # SQLParseError. Regular parse errors are embedded in the MatchResult.
                try:
                    if _prof is not None:
                        _ts = time.perf_counter()
                    rs_match = self._rs_parser.parse_match_result_from_tokens(tokens)
                    if _prof is not None:
                        _prof["rust_core"] = time.perf_counter() - _ts
                except RsParseError as e:
                    # Convert Rust parse error to SQLParseError with position info
                    raise SQLParseError.from_rs_parse_error(
                        e, segments[_start_idx:_end_idx]
                    ) from e

                # Build the BaseSegment tree from the Rust match result.
                # PYTHON PARITY: only the code portion (segments[_start_idx:_end_idx])
                # is passed, since match-result indices are relative to it.
                code_segments = segments[_start_idx:_end_idx]
                if _NATIVE_AST_ENABLED:
                    # Fused path: instantiate segments directly from rs_match in a
                    # single pass (no intermediate Python MatchResult tree).
                    if _prof is not None:
                        _ts = time.perf_counter()
                    _matched = self._apply_rs_match_result(
                        rs_match, code_segments, parse_context
                    )
                    if _prof is not None:
                        _prof["apply"] = time.perf_counter() - _ts
                else:
                    # Legacy path: rebuild a Python MatchResult, then apply it.
                    if _prof is not None:
                        _ts = time.perf_counter()
                    match = self._convert_rs_match_result(rs_match, code_segments)
                    if _prof is not None:
                        _prof["convert"] = time.perf_counter() - _ts
                    parser_logger.info("Root Match:\n%s", match)

                    if _prof is not None:
                        _ts = time.perf_counter()
                    _matched = match.apply(code_segments, parse_context=parse_context)
                    if _prof is not None:
                        _prof["apply"] = time.perf_counter() - _ts

                # PYTHON PARITY: Add back any unmatched segments after the match.
                # matched_slice/truthiness are read from rs_match so both build
                # paths agree (mirrors MatchResult.matched_slice / __bool__).
                _m_start, _m_stop = rs_match.matched_slice
                _match_truthy = _m_stop > _m_start or bool(rs_match.insert_segments)
                matched_stop = _start_idx + _m_stop
                _unmatched = segments[matched_stop:_end_idx]

                # PYTHON PARITY: If there are unmatched code segments, wrap them in
                # UnparsableSegment. This matches the logic in FileSegment.root_parse()
                content: tuple[BaseSegment, ...]
                if not _match_truthy:
                    parse_context.increment_parse_nodes()
                    content = (
                        UnparsableSegment(
                            segments[_start_idx:_end_idx],
                            expected=str(self.RootSegment.match_grammar),
                        ),
                    )
                elif _unmatched:
                    _idx = 0
                    for idx, seg in enumerate(_unmatched):
                        if seg.is_code:
                            _idx = idx
                            break
                    else:  # pragma: no cover
                        _idx = len(_unmatched)
                    parse_context.increment_parse_nodes()
                    content = (
                        _matched
                        + _unmatched[:_idx]
                        + (
                            UnparsableSegment(
                                _unmatched[_idx:],
                                expected="Nothing else in FileSegment.",
                            ),
                        )
                    )
                else:
                    content = _matched + _unmatched

                parse_context.increment_parse_nodes()
                result = self.RootSegment(
                    segments[:_start_idx] + content + segments[_end_idx:], fname=fname
                )

                # Build the mutable Rust arena tree (RsTree) from the MatchResult.
                # This is the id-addressable façade tree (RsTree/RsHandle) used by
                # Rust-side linting/fixing to avoid round-tripping through Python's
                # segment tree.
                try:
                    # Extract leading non-code tokens (segments before _start_idx:
                    # whitespace/newlines at the start of the file) so the arena's
                    # flat raw list matches Python's raw_segments ordering exactly.
                    leading_tokens = (
                        self._extract_tokens_from_segments(segments[:_start_idx])
                        if _start_idx
                        else []
                    )
                    # Extract trailing non-code tokens (segments after _end_idx: newline,
                    # end_of_file, etc.) and include them in the arena so that the
                    # reflow/respace rules can correctly detect EOF and trailing newlines.
                    trailing_tokens = (
                        self._extract_tokens_from_segments(segments[_end_idx:])
                        if _end_idx < len(segments)
                        else []
                    )
                    if _prof is not None:
                        _ts = time.perf_counter()
                    result._rs_tree = rs_match.apply_as_tree(
                        tokens,
                        leading=leading_tokens,
                        trailing=trailing_tokens,
                    )
                    if _prof is not None:
                        _prof["apply_as_tree"] = time.perf_counter() - _ts
                except Exception:  # pragma: no cover
                    # Non-critical: if tree building fails, rules fall back to Python
                    parser_logger.warning(
                        f"Unable to apply match result in parse tree for {fname}, falling"
                        " back to Python. Please report this as a bug with the SQL that"
                        " caused it."
                    )
                    result._rs_tree = None

                # Accumulate this variant's per-stage timings into the profile
                # (summing across rendered variants of the same source).
                if _prof is not None:
                    for _stage, _dur in _prof.items():
                        _PARSE_PROFILE[_stage] = _PARSE_PROFILE.get(_stage, 0.0) + _dur

                if parse_statistics:  # pragma: no cover
                    print(
                        "Warning: parse_statistics not yet implemented for Rust parser"
                    )

                return result
            except SQLParseError as err:
                if err.segment is None:
                    anchor = next((seg for seg in segments if seg.is_code), None)
                    if anchor is not None:
                        err = SQLParseError(
                            description=err.description,
                            segment=anchor,
                            ignore=err.ignore,
                            fatal=err.fatal,
                            warning=err.warning,
                        )
                raise err

        @functools.lru_cache(maxsize=128)
        def _get_segment_class_by_name(
            self, segment_name: str
        ) -> Optional[type[BaseSegment]]:
            """Get a segment class by its exact class name from the dialect.

            Args:
                segment_name: The segment CLASS name (e.g., "AsAliasOperatorSegment")

            Returns:
                The segment class, or None if not found or is a grammar

            Note:
                Results are cached per parser instance since dialect is fixed.
            """
            if segment_name == "UnparsableSegment":
                return UnparsableSegment

            # Get the item from the dialect library
            dialect: Dialect = self.config.get("dialect_obj")
            item = dialect.get_segment(segment_name)

            # Verify it's a valid segment class (not a grammar element)
            if (
                item is not None
                and isinstance(item, type)
                and issubclass(item, BaseSegment)
            ):
                return item

            # Not a valid segment class - return None for grammar names
            return None  # pragma: no cover

        def _rs_match_fields(
            self, rs_match: "RsMatchResult"
        ) -> tuple[
            Optional[type["BaseSegment"]],
            dict[str, Any],
            tuple[tuple[int, type], ...],
        ]:
            """Extract (matched_class, segment_kwargs, insert_segments) from a match.

            Shared by both tree-building paths: _convert_rs_match_result (the
            MatchResult-based path) and _apply_rs_match_result (the fused path).
            """
            # Determine matched_class. The Rust parser includes the actual Python
            # class names (from codegen) in matched_class, so we use them directly.
            matched_class: Optional[type["BaseSegment"]] = (
                self._get_segment_class_by_name(rs_match.matched_class)
                if rs_match.matched_class
                else None
            )

            # Build segment_kwargs - optimize by checking first if we need any
            segment_kwargs: dict[str, Any] = {}
            if rs_match.instance_types:
                segment_kwargs["instance_types"] = tuple(rs_match.instance_types)

            # Copy over any segment_kwargs from Rust
            # (e.g., "expected" for UnparsableSegment)
            if rs_match.segment_kwargs:
                segment_kwargs.update(rs_match.segment_kwargs)

            # Set trim_chars from the match result if available
            if rs_match.trim_chars:
                segment_kwargs["trim_chars"] = tuple(rs_match.trim_chars)

            # Set casefold from the match result if available
            if rs_match.casefold:
                if rs_match.casefold == "upper":
                    segment_kwargs["casefold"] = str.upper
                elif rs_match.casefold == "lower":
                    segment_kwargs["casefold"] = str.lower

            # Set quoted_value and escape_replacements for normalization
            if rs_match.quoted_value:  # pragma: no cover
                segment_kwargs["quoted_value"] = rs_match.quoted_value
            if rs_match.escape_replacements:  # pragma: no cover
                segment_kwargs["escape_replacements"] = rs_match.escape_replacements

            # Extract insert_segments (Indent/Dedent meta segments).
            # rs_match.insert_segments contains (idx, seg_type, is_implicit) tuples;
            # these are pre-flattened on the Rust side.
            insert_segments: tuple[tuple[int, type], ...] = ()
            if rs_match.insert_segments:
                insert_segments = tuple(
                    (
                        idx,
                        (
                            ImplicitIndent
                            if (seg_type == "indent" and is_implicit)
                            else (Indent if seg_type == "indent" else Dedent)
                        ),
                    )
                    for idx, seg_type, is_implicit in rs_match.insert_segments
                )

            return matched_class, segment_kwargs, insert_segments

        def _convert_rs_match_result(
            self,
            rs_match: "RsMatchResult",
            segments: tuple["BaseSegment", ...],
            depth: int = 0,
        ) -> MatchResult:
            """Convert Rust MatchResult to Python MatchResult.

            Args:
                rs_match: RsMatchResult from Rust parser
                segments: Segment array for error reporting
                depth: Current recursion depth for debugging

            Returns:
                Python MatchResult with equivalent structure

            """
            start, stop = rs_match.matched_slice
            matched_class, segment_kwargs, insert_segments = self._rs_match_fields(
                rs_match
            )

            # Convert child matches recursively
            # Note: Transparent grammar nodes are now flattened on the Rust side,
            # so we don't need to do it here anymore
            #
            # NOTE: Keep this a plain loop rather than a generator expression:
            # a genexpr would add its own stack frame per nesting level on top
            # of this recursive call, which halves the safe recursion depth.
            # Matches _apply_rs_match_result's plain for loop below, so both
            # AST-building paths tolerate the same nesting depth.
            child_matches_list = []
            for child in rs_match.child_matches:
                child_matches_list.append(
                    self._convert_rs_match_result(child, segments, depth + 1)
                )
            child_matches = tuple(child_matches_list)

            return MatchResult(
                matched_slice=slice(start, stop),
                matched_class=matched_class,
                child_matches=child_matches,
                segment_kwargs=segment_kwargs,
                insert_segments=insert_segments,
            )

        def _apply_rs_match_result(
            self,
            rs_match: "RsMatchResult",
            segments: tuple["BaseSegment", ...],
            parse_context: ParseContext,
        ) -> tuple["BaseSegment", ...]:
            """Build BaseSegments directly from an RsMatchResult in a single pass.

            This fuses _convert_rs_match_result and MatchResult.apply: instead of
            rebuilding the whole match tree as Python MatchResult objects and then
            walking it again, it walks the RsMatchResult once and instantiates the
            BaseSegment tree directly.

            The algorithm mirrors MatchResult.apply() exactly (including the
            parse-node accounting), so it produces an identical tree.
            """
            start, stop = rs_match.matched_slice
            matched_class, segment_kwargs, insert_segments = self._rs_match_fields(
                rs_match
            )

            # NOTE: Accumulate into a list and build the tuple once at the end.
            # `tuple += ...` looks equivalent but isn't: tuples are immutable,
            # so each `+=` allocates a new tuple and copies everything
            # accumulated so far, making a loop of N appends O(N^2). A list
            # amortises appends/extends to O(N), which matters here since this
            # runs at every level of a potentially large tree (e.g. long
            # column/UNION/IN lists produce nodes with many trigger locations).
            result_segments_list: list[BaseSegment] = []

            # Zero-length match: only meta inserts are valid (mirrors apply()).
            # NOTE: Unreachable in practice since the Rust parser stopped
            # emitting zero-length meta child matches (Bracketed now drops
            # direct-child metas for Python parity). Kept as the defensive
            # mirror of apply()'s zero-length branch, including its
            # parse-node accounting.
            if start == stop:  # pragma: no cover
                for idx, seg in insert_segments:
                    assert idx == start, (
                        f"Tried to insert @{idx} outside of matched "
                        f"slice {(start, stop)}"
                    )
                    _pos = _get_point_pos_at_idx(segments, idx)
                    parse_context.increment_parse_nodes()
                    result_segments_list.append(seg(pos_marker=_pos))
                return tuple(result_segments_list)

            # Merge inserts (added first) and child matches into trigger locations.
            trigger_locs: defaultdict[int, list[Union["RsMatchResult", type]]] = (
                defaultdict(list)
            )
            for idx, seg in insert_segments:
                trigger_locs[idx].append(seg)
            for child in rs_match.child_matches:
                trigger_locs[child.matched_slice[0]].append(child)

            max_idx = start
            for idx in sorted(trigger_locs):
                # Include any untouched segments before this trigger.
                if idx > max_idx:
                    result_segments_list.extend(segments[max_idx:idx])
                    max_idx = idx
                elif idx < max_idx:  # pragma: no cover
                    # An outer match contains overlapping child matches: the
                    # Rust parser emitted inconsistent ranges (mirrors apply()).
                    raise ValueError(
                        "Segment skip ahead error. An outer match contains "
                        "overlapping child matches. This MatchResult was "
                        "wrongly constructed."
                    )
                for trigger in trigger_locs[idx]:
                    if isinstance(trigger, type):
                        # A meta segment class (Indent/Dedent/ImplicitIndent).
                        # NOTE: apply() does not count meta inserts here (only in
                        # the zero-length branch above), so neither do we.
                        _pos = _get_point_pos_at_idx(segments, idx)
                        result_segments_list.append(trigger(pos_marker=_pos))
                    else:
                        # A child match - recurse and advance past it.
                        result_segments_list.extend(
                            self._apply_rs_match_result(
                                trigger, segments, parse_context
                            )
                        )
                        max_idx = trigger.matched_slice[1]

            # Anything left after the last trigger.
            if max_idx < stop:
                result_segments_list.extend(segments[max_idx:stop])

            result_segments = tuple(result_segments_list)

            if not matched_class:
                return result_segments

            new_seg = matched_class.from_result_segments(
                result_segments, segment_kwargs
            )
            parse_context.increment_parse_nodes()
            return (new_seg,)

        @staticmethod
        def _template_segment_to_rstoken(segment: TemplateSegment) -> "RsToken":
            """Convert a Python TemplateSegment to a Rust RsToken.

            Creates a template placeholder token with the segment's metadata.
            This allows the Rust parser to handle templated SQL (Jinja, dbt, etc.).

            Args:
                segment: Python TemplateSegment from the lexer

            Returns:
                RsToken representing a template placeholder
            """
            # Extract position marker data
            pm = segment.pos_marker
            source_slice = (pm.source_slice.start, pm.source_slice.stop)
            templated_slice = (pm.templated_slice.start, pm.templated_slice.stop)
            templated_file = pm.templated_file

            # Convert block_uuid to hex string if present
            block_uuid_str = segment.block_uuid.hex if segment.block_uuid else None

            # Create template placeholder token using Rust constructor
            return RsToken.template_placeholder_from_slice(
                source_slice=source_slice,
                templated_slice=templated_slice,
                block_type=segment.block_type,
                _source_str=segment.source_str,  # Passed for API compatibility
                block_uuid=block_uuid_str,
                templated_file=templated_file,
            )

        def _extract_tokens_from_segments(
            self, segments: tuple["BaseSegment", ...]
        ) -> list["RsToken"]:
            """Extract RsToken objects from RawSegments.

            This extracts the cached _rstoken attribute from segments that came from
            the Rust lexer, or converts TemplateSegments to template placeholder tokens.

            Args:
                segments: Tuple of BaseSegment objects

            Returns:
                List of RsToken objects (or compatible token objects)
            """
            tokens = []
            for segment in segments:
                # Check if segment has _rstoken attribute (cached original token)
                if hasattr(segment, "_rstoken"):
                    tokens.append(segment._rstoken)
                elif isinstance(segment, TemplateSegment):
                    # Template segment - create template placeholder token
                    tokens.append(self._template_segment_to_rstoken(segment))
                else:  # pragma: no cover
                    # Cannot reconstruct RsToken from Python segment
                    raise ValueError(
                        f"Cannot extract RsToken from segment {segment!r}. "
                        f"Unsupported segment type: {type(segment).__name__}."
                    )

            return tokens

except ImportError:
    RustParser = None  # type: ignore[assignment, misc]
    _HAS_RUST_PARSER = False
