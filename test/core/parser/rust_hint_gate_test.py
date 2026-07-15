"""Guard test for the Rust "first-token hint gate" optimisation.

The Rust parser's table-driven `Sequence` and `Delimited` handlers (see
`sqlfluffrs_parser/src/parser/table_driven/sequence.rs` and `delimited.rs`)
skip creating a real child frame for an element when
`Parser::simple_hint_rejects` (`sqlfluffrs_parser/src/parser/helpers.rs`)
proves the element's first-token `simple()` hint cannot match at the
current position. When the gate fires it synthesises an *empty* match
result for that element, exactly as if a real child frame had run and
failed.

That synthesis is unsound for a plain (non-`Bracketed`) `Sequence` whose own
`parse_mode` is `ParseMode.GREEDY`: per `Sequence.match()`
(`sqlfluff/core/parser/grammar/sequence.py`), when such a sequence's first
required element completely fails to match, it does not return an empty
match - it returns a *non-empty* result wrapped as an `UnparsableSegment`
spanning up to the sequence's own `max_idx`. A first-token hint mismatch
therefore does not, in general, guarantee an empty result for this kind of
grammar, which the Rust gate's "hint rejects => treat as empty" assumption
requires. `Bracketed` is exempt because it overrides both `simple()` and
`match()` to check the bracket token directly instead of delegating to
`Sequence`'s structural hint.

No shipped dialect grammar exercises this today: every bare
`Sequence(parse_mode=ParseMode.GREEDY)` is reachable only inside a
`Bracketed`, or has `simple() is None` (too complex to hint, so the Rust
gate is a no-op for it - see `simple_hint_rejects`'s early return when
`get_simple_hint_for_grammar` finds nothing). This test walks every
dialect's grammar library looking for that combination and fails loudly the
day a new dialect rule introduces it, so the gate logic (or the new
grammar) gets a second look before the gap actually reproduces.
"""

from sqlfluff.core import FluffConfig
from sqlfluff.core.dialects import dialect_readout, dialect_selector
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar.anyof import AnyNumberOf
from sqlfluff.core.parser.grammar.base import Ref
from sqlfluff.core.parser.grammar.sequence import Bracketed, Sequence
from sqlfluff.core.parser.types import ParseMode


def _find_reachable_greedy_hinted_sequences(dialect, parse_context):
    """Collect every plain `Sequence` reachable in `dialect` that is both.

    - `parse_mode == ParseMode.GREEDY` (not `Bracketed`, which is immune), and
    - has a non-``None`` `simple()` hint (the only case the Rust hint gate
      can actually act on - see `simple_hint_rejects`).

    Walks `Ref`/`Sequence`/`AnyNumberOf`/`Bracketed` (and segment
    `match_grammar`/`parse_grammar`) recursively, memoising by `Ref` name
    and grammar object identity so shared sub-grammars (e.g. expressions
    referenced from hundreds of places) are only visited once.
    """
    offenders = []
    visited_ref_names = set()
    visited_ids = set()

    def walk(grammar):
        if grammar is None:
            return
        if isinstance(grammar, type):
            # A Segment class: descend into its top-level grammar.
            key = ("class", grammar)
            if key in visited_ids:
                return
            visited_ids.add(key)
            walk(getattr(grammar, "match_grammar", None))
            walk(getattr(grammar, "parse_grammar", None))
            return
        if isinstance(grammar, Ref):
            if grammar._ref in visited_ref_names:
                return
            visited_ref_names.add(grammar._ref)
            try:
                target = grammar._get_elem(dialect=dialect)
            except Exception:
                # Unresolvable ref (e.g. dialect doesn't define it) - not
                # this test's concern.
                return
            walk(target)
            return
        if id(grammar) in visited_ids:
            return
        visited_ids.add(id(grammar))
        if isinstance(grammar, Bracketed):
            # Immune itself, but its content elements are not.
            for elem in getattr(grammar, "_elements", ()):
                walk(elem)
            return
        if isinstance(grammar, Sequence):
            if getattr(grammar, "parse_mode", None) == ParseMode.GREEDY:
                try:
                    hint = grammar.simple(parse_context=parse_context)
                except Exception:
                    hint = None
                if hint is not None:
                    offenders.append(grammar)
            for elem in getattr(grammar, "_elements", ()):
                walk(elem)
            return
        if isinstance(grammar, AnyNumberOf):
            # Covers OneOf and Delimited too (both subclass AnyNumberOf).
            for elem in getattr(grammar, "_elements", ()):
                walk(elem)
            return
        # Leaf parsers, Meta, Conditional, Anything, Nothing: nothing to
        # recurse into.

    for grammar_or_class in dialect._library.values():
        walk(grammar_or_class)

    return offenders


def test__rust_hint_gate__no_reachable_greedy_hinted_sequence():
    """No dialect may expose a hinted, non-Bracketed GREEDY Sequence.

    If this test starts failing, a new (or changed) dialect rule has
    introduced a grammar the Rust first-token hint gate handles
    incorrectly (see module docstring). Before "fixing" this test by
    special-casing the new grammar, fix the underlying gate assumption in
    `sqlfluffrs_parser`'s `simple_hint_rejects`/`sequence.rs`/`delimited.rs`,
    or restructure the offending grammar so it is no longer reachable in
    this shape (e.g. wrap it in `Bracketed`, or make its first element
    complex enough that `simple()` returns `None`).
    """
    all_offenders = []
    for entry in dialect_readout():
        dialect_name = entry.label
        dialect = dialect_selector(dialect_name)
        config = FluffConfig(overrides=dict(dialect=dialect_name))
        parse_context = ParseContext.from_config(config)
        offenders = _find_reachable_greedy_hinted_sequences(dialect, parse_context)
        all_offenders.extend((dialect_name, repr(g)) for g in offenders)

    assert not all_offenders, (
        "Found grammar(s) that are reachable, plain (non-Bracketed) "
        "Sequences with parse_mode=GREEDY and a non-None simple() hint. "
        "The Rust first-token hint gate (simple_hint_rejects in "
        "sqlfluffrs_parser) assumes a hint-rejected element always "
        "produces an empty match, which does not hold for this kind of "
        "sequence - see this test module's docstring for why, and fix the "
        "gate (or the grammar) before merging: " + repr(all_offenders)
    )


def test__rust_hint_gate__detector_flags_synthetic_greedy_sequence():
    """Prove the detector itself works, not just that today's count is zero.

    A "no offenders found" result is only meaningful if the walker can
    actually find one. This constructs a synthetic offending grammar (a
    bare hinted GREEDY Sequence) and a synthetic safe one (the same
    Sequence in STRICT mode) and checks the detector tells them apart.
    """
    from sqlfluff.core.parser.parsers import StringParser
    from sqlfluff.core.parser.segments.raw import RawSegment

    config = FluffConfig(overrides=dict(dialect="ansi"))
    parse_context = ParseContext.from_config(config)

    class _FakeDialect:
        def __init__(self, library):
            self._library = library

    offending_seq = Sequence(
        StringParser("FOO", RawSegment, type="keyword"), parse_mode=ParseMode.GREEDY
    )
    offenders = _find_reachable_greedy_hinted_sequences(
        _FakeDialect({"FakeGrammar": offending_seq}), parse_context
    )
    assert offenders == [offending_seq]

    safe_seq = Sequence(
        StringParser("FOO", RawSegment, type="keyword"), parse_mode=ParseMode.STRICT
    )
    offenders = _find_reachable_greedy_hinted_sequences(
        _FakeDialect({"FakeGrammar": safe_seq}), parse_context
    )
    assert offenders == []
