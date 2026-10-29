"""Parity tests that need Python-side instrumentation.

Most parity coverage is data-driven (see ``cases_test.py`` and
``test/fixtures/parity/``). The tests here can't be expressed as a plain
SQL-plus-config case because they instrument the Python side: codegen
object-lifetime probes, subprocess hash-seed probes.
"""

import gc
import os
import subprocess
import sys
import weakref
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[4]


def test__parity__codegen_grammar_cache_pins_against_gc():
    """A grammar cached by TableBuilder must not be collectible.

    utils/build_parsers.py's TableBuilder deduplicates flattened grammars in
    ``grammar_to_id``, keyed by Python's id() - the object's raw memory
    address. That's only a valid cache key for as long as the object stays
    alive: once it's garbage-collected, CPython is free to hand that same
    address to an unrelated later grammar, which then silently inherits the
    stale cache entry - wiring a semantically wrong subgrammar into the
    generated Rust dialect tables (seen for real in oracle's
    ``Ref("AttributeIndicatorSegment")`` picking up a dead
    ``Ref("ModuloSegment")`` entry). The builder must keep every grammar it
    caches alive for its own lifetime so no id() in ``grammar_to_id`` can
    ever be freed and reused.
    """
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from sqlfluff.core.dialects import dialect_selector
    from sqlfluff.core.parser.grammar.base import Ref
    from utils.build_parsers import DummyParseContext, TableBuilder

    dialect = dialect_selector("ansi")
    ctx = DummyParseContext(dialect=dialect, uuid=0)
    builder = TableBuilder()

    grammar = Ref("SelectStatementSegment")
    alive = weakref.ref(grammar)
    builder.flatten_grammar(grammar, ctx)

    del grammar
    gc.collect()

    assert alive() is not None, (
        "TableBuilder let a cached grammar get garbage-collected - its "
        "id() can now be reused by an unrelated grammar, silently aliasing "
        "it to this stale GrammarId."
    )


def test__parity__codegen_lexer_patterns_hash_seed_stable():
    """Dialect lexer regexes are byte-identical across interpreter hash seeds.

    Regression guard: tsql's money-literal lexer pattern used to be assembled
    from an unordered set of currency symbols via ``"".join(...)`` with no
    sorting, so its bytes shuffled with the interpreter's hash seed - unlike
    every other ``dialect.sets(...)``-derived pattern in the codebase, which
    already sorts first. That made the generated Rust lexer file (produced by
    utils/rustify.py) unreproducible: rebuilding with a different hash seed
    silently changed the checked-in output's byte content, even though the
    character class matched exactly the same input either way. The join is now
    sorted; this test keeps it that way.
    """
    script = (
        "from sqlfluff.core.dialects import dialect_selector\n"
        "d = dialect_selector('tsql')\n"
        "for m in d.lexer_matchers:\n"
        "    print(m.name, repr(getattr(m, 'template', None)))\n"
    )
    outputs = set()
    for seed in ("0", "1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONIOENCODING="utf-8")
        proc = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            env=env,
            check=True,
            timeout=120,
        )
        outputs.add(proc.stdout)
    assert len(outputs) == 1, "lexer matcher patterns vary with the hash seed"


@pytest.mark.parametrize("dialect_name", ["ansi", "postgres", "tsql"])
def test__parity__codegen_hint_table_matches_python(dialect_name):
    """The generated hint table says exactly what each grammar's simple() says.

    simple() has three answers, and the Rust tables must keep them apart:
    None (no hint, try a full match) is NO_SIMPLE_HINT; an empty hint (can
    never match, e.g. Nothing) is an entry with no words and no types; any
    other hint is an entry that decodes back to its words and types.
    Rust prunes options and scans for terminators with these, so a hint that
    decodes differently makes Rust try or skip different grammars from Python.
    """
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from sqlfluff.core.dialects import dialect_selector
    from utils.build_parsers import DummyParseContext, TableBuilder

    dialect = dialect_selector(dialect_name)
    ctx = DummyParseContext(dialect=dialect, uuid=0)
    builder = TableBuilder()
    recorded = []
    add_simple_hint = builder._add_simple_hint

    def recording_add_simple_hint(grammar, parse_context):
        hint_id = add_simple_hint(grammar, parse_context)
        recorded.append((grammar, hint_id))
        return hint_id

    builder._add_simple_hint = recording_add_simple_hint
    for _, element in sorted(dialect._library.items()):
        builder.flatten_grammar(element, ctx)

    def decode(start, count):
        return frozenset(
            builder.strings[builder.hint_string_indices[i]]
            for i in range(start, start + count)
        )

    states = {"none": 0, "empty": 0, "words or types": 0}
    for grammar, hint_id in recorded:
        try:
            expected = grammar.simple(ctx)
        except (RuntimeError, AttributeError):
            # The builder records these as no hint, the same as None: a raw
            # segment class such as LiteralSegment has no match_grammar.
            expected = None
        if hint_id is None:
            assert expected is None, grammar
            states["none"] += 1
            continue
        assert 0 <= hint_id < len(builder.simple_hints), (grammar, hint_id)
        data = builder.simple_hints[hint_id]
        decoded = (
            decode(data.raw_values_start, data.raw_values_count),
            decode(data.token_types_start, data.token_types_count),
        )
        assert decoded == expected, grammar
        states[
            "empty" if decoded == (frozenset(), frozenset()) else "words or types"
        ] += 1

    # Every state actually occurs, so the test can't pass by checking nothing.
    assert all(states.values()), states
