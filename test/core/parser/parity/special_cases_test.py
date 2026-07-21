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
