"""Shared capture and comparison logic for the Python-vs-Rust parity suite.

Parity tests are differential: the same input runs through two (or three)
engine paths, and the results should match exactly. Each surface (parse,
templated parse, lex) has one capture function, and each records at maximum
strictness:

* the tree in tuple form, with raws, metas and position markers,
* ``stringify()`` bytes (carrying UnparsableSegment "Expected:" messages),
* the raw round-trip,
* the normalization kwargs carried by every segment
  (quoted_value / escape_replacements / trim_chars / casefold),
* the full ``class_types`` chain of every leaf segment (not just its
  primary ``get_type()``, which is all ``to_tuple()``/``stringify()`` see),
* whether the tree contains an ``UnparsableSegment`` anywhere,
* or, for a raised exception, its type, message and ``SQLBaseError``
  position/flag attributes (``PanicException`` is a BaseException, so every
  raising path is caught).

Known differences are handled per-case in the fixture corpus
(``test/fixtures/parity/*.yml``) with an explicit, reasoned ``xfail`` entry,
keeping every pinned repro at the same strictness. That's also why fixing
an engine gap flips CI: the strict xfail then reports as an unexpected pass.

The engine legs compared:

* ``python_vs_rust``  - pure-Python ``Parser`` vs ``RustParser`` (legacy
  convert+apply build path). The Python parser is the reference.
* ``native_vs_legacy`` - ``RustParser``'s fused native-AST build path vs its
  legacy convert+apply path. Both consume the same Rust match result, so any
  difference points to a bug in one of the two builders.
* ``lexer``           - ``PyLexer`` vs ``PyRsLexer`` token streams.
* ``invariants``      - structural well-formedness of raw ``RsMatchResult``
  trees, checked directly rather than compared (a violation is a rust-core
  bug by definition).

Python-vs-native parity follows transitively from the two parser legs.
"""

from functools import lru_cache
from pathlib import Path

import pytest
import yaml

try:
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER, RustParser
except ImportError:  # pragma: no cover
    _HAS_RUST_PARSER = False
    RustParser = None

requires_rust_parser = pytest.mark.skipif(
    not _HAS_RUST_PARSER, reason="Rust parser not available"
)

_TEST_DIR = Path(__file__).resolve().parents[3]
PARITY_CASE_DIR = _TEST_DIR / "fixtures" / "parity"
DIALECT_FIXTURE_DIR = _TEST_DIR / "fixtures" / "dialects"

_TREE_TUPLE_KWARGS = dict(
    code_only=False, show_raw=True, include_meta=True, include_position=True
)

# The parser-leg engines, keyed by (left, right) per leg. The right-hand
# engine is the reference the left-hand one must match.
PARSER_LEGS = {
    "python_vs_rust": ("rust", "python"),
    "native_vs_legacy": ("rust-native", "rust"),
}


def _normalize_kwarg(value):
    # ``casefold`` holds a callable (e.g. ``str.upper``); compare by name.
    return getattr(value, "__qualname__", value) if callable(value) else value


def _tree_fingerprints(tree):
    """Compute the three re-walk fingerprints of a tree in a single pass.

    Captured per tree, and each of these would otherwise re-crawl the whole
    thing (``recursive_crawl_all`` twice plus a ``recursive_crawl`` for the
    unparsable check). Folding them into one walk keeps the captures identical
    while paying for the traversal once:

    * ``segment_kwargs`` - the normalization kwargs carried by each segment
      that has any. Rules like RF06 use these (e.g. for quote normalization);
      they stay hidden from ``to_tuple()`` and ``stringify()``, yet an engine
      difference here still shows up through rule behaviour.
    * ``has_unparsable`` - whether any ``UnparsableSegment`` is present
      (``is_type("unparsable")`` over the full crawl is equivalent to
      ``any(recursive_crawl("unparsable"))``: both consider self and all
      descendants).
    * ``class_types`` - the full ``class_types`` set of every leaf segment.
      ``to_tuple()``/``stringify()`` only record ``get_type()`` (the primary
      type); a bare-class ``Ref`` wrapping a matched token in an ANCESTOR
      class can produce the right primary type via ``instance_types`` while
      still losing class-level types from the token's own lineage - invisible
      to a ``to_tuple()``/``stringify()`` comparison alone (#8138).
    """
    segment_kwargs = []
    class_types = []
    has_unparsable = False
    for seg in tree.recursive_crawl_all():
        kwargs = tuple(
            _normalize_kwarg(getattr(seg, attr, None))
            for attr in (
                "quoted_value",
                "escape_replacements",
                "trim_chars",
                "casefold",
            )
        )
        if any(value is not None for value in kwargs):
            segment_kwargs.append((seg.raw, *kwargs))
        if not seg.segments:
            class_types.append((seg.raw, tuple(sorted(seg.class_types))))
        if seg.is_type("unparsable"):
            has_unparsable = True
    return segment_kwargs, has_unparsable, class_types


def _exception_capture(err):
    return (
        "exc",
        type(err).__name__,
        str(err),
        getattr(err, "line_no", None),
        getattr(err, "line_pos", None),
        getattr(err, "fatal", None),
        getattr(err, "ignore", None),
        getattr(err, "warning", None),
    )


def _tree_capture(tree):
    segment_kwargs, has_unparsable, class_types = _tree_fingerprints(tree)
    return (
        "tree",
        tree.to_tuple(**_TREE_TUPLE_KWARGS),
        tree.stringify(),
        tree.raw,
        segment_kwargs,
        has_unparsable,
        class_types,
    )


@lru_cache(maxsize=None)
def _base_config(dialect):
    """A fully-expanded FluffConfig for a dialect, cached across the suite.

    Constructing a FluffConfig expands the dialect grammar (the expensive part,
    ~3.5ms); ``.copy()`` shares that expanded ``dialect_obj`` and only re-copies
    the small ``_configs`` dict (~0.15ms). The dialect-corpus sweep alone builds
    one config per fixture (thousands), so caching the base and copying it saves
    the bulk of that work.
    """
    from sqlfluff.core import FluffConfig

    return FluffConfig(overrides={"dialect": dialect})


def build_config(dialect="ansi", configs=None, extra_overrides=None):
    """Build a FluffConfig from a parity case's dialect/configs fields.

    ``configs`` keys are either plain override names (e.g. ``max_parse_depth``)
    or dotted section paths (e.g. ``indentation.indented_joins``) applied via
    ``set_value`` - which mirrors how ini-file values arrive (int-typed, not
    bool), a distinction at least one pinned bug depends on.
    """
    from sqlfluff.core import FluffConfig

    # Fast path: a plain dialect (no extra overrides, no configs) is the
    # overwhelming majority of calls. Hand out a cheap copy of the cached base
    # so the dialect is expanded once per dialect, not once per fixture. The
    # copy is independently mutable, so callers stay isolated.
    if not configs and not extra_overrides:
        return _base_config(dialect).copy()

    overrides = {"dialect": dialect}
    overrides.update(extra_overrides or {})
    dotted = {}
    for key, value in (configs or {}).items():
        if "." in key:
            dotted[key] = value
        else:
            overrides[key] = value
    config = FluffConfig(overrides=overrides)
    for key, value in dotted.items():
        config.set_value(key.split("."), value)
    return config


def parse_capture(engine, config, segments, fname="t.sql"):
    """Parse pre-lexed segments with one engine; capture at full strictness.

    ``engine`` is ``python`` (pure-Python ``Parser``), ``rust`` (``RustParser``
    legacy convert+apply path) or ``rust-native`` (``RustParser`` fused
    native-AST path).
    """
    from sqlfluff.core.parser import Parser
    from sqlfluff.core.parser.rust_parser import get_native_ast, set_native_ast

    parser_cls = Parser if engine == "python" else RustParser
    previous_native_ast = get_native_ast()
    # Pin the native-AST flag to exactly this leg, never the ambient global:
    # the 'rust' (legacy) leg must run with it OFF even when the environment
    # (SQLFLUFF_RS_NATIVE_AST) has turned it on, or native_vs_legacy compares
    # the native builder against itself.
    set_native_ast(engine == "rust-native")
    try:
        tree = parser_cls(config=config).parse(segments, fname=fname)
    except BaseException as err:  # PanicException is a BaseException
        return _exception_capture(err)
    finally:
        set_native_ast(previous_native_ast)
    if tree is None:
        return ("none",)
    return _tree_capture(tree)


def linted_parse_capture(engine, sql, dialect="ansi", configs=None, context=None):
    """Template+lex+parse ``sql`` through the Linter with one engine.

    Used for templated cases: TemplateSegment placeholder tokens and the
    Linter-driven parse path can't be reached by ``parse_capture``. Captures
    the tree at full strictness plus all violations. Jinja block UUIDs are
    freshly randomized on every lex, so they are normalized out of the
    stringify comparison.
    """
    import re

    from sqlfluff.core import Linter
    from sqlfluff.core.parser.rust_parser import get_native_ast, set_native_ast

    config = build_config(
        dialect=dialect,
        configs=configs,
        extra_overrides={
            "templater": "jinja",
            "rules": "none",
            "use_rust_parser": engine != "python",
        },
    )
    for key, value in (context or {}).items():
        config.set_value(["templater", "jinja", "context", key], value)

    previous_native_ast = get_native_ast()
    # See parse_capture: pin the flag to this leg, never the ambient global.
    set_native_ast(engine == "rust-native")
    try:
        parsed = Linter(config=config).parse_string(sql, fname="t.sql")
    except BaseException as err:  # PanicException is a BaseException
        return {"violations": [], "tree": None, "exc": _exception_capture(err)}
    finally:
        set_native_ast(previous_native_ast)

    # A template that fails to render yields no parsed variants, and the
    # .tree property asserts on that - treat it as tree=None (the violations
    # then carry the templating error for comparison).
    tree = parsed.tree if parsed.parsed_variants else None
    capture = {
        "violations": [(type(v).__name__, str(v)) for v in parsed.violations],
        "tree": None,
    }
    if tree is not None:
        segment_kwargs, has_unparsable, class_types = _tree_fingerprints(tree)
        capture["tree"] = tree.to_tuple(**_TREE_TUPLE_KWARGS)
        capture["stringify"] = re.sub(
            r"Block: '[0-9a-f]+'", "Block: '<uuid>'", tree.stringify()
        )
        capture["raw"] = tree.raw
        capture["segment_kwargs"] = segment_kwargs
        capture["has_unparsable"] = has_unparsable
        capture["class_types"] = class_types
    return capture


def _linted_capture_as_tuple(capture):
    """Adapt linted_parse_capture's dict shape to check_expectations's shape.

    Lets templated cases share the same expectation checks as plain parser
    cases.
    """
    if capture.get("exc") is not None:
        return capture["exc"]
    if capture["tree"] is None:
        message = "; ".join(msg for _, msg in capture["violations"])
        return ("exc", "TemplateOrParseFailure", message, None, None, None, None, None)
    return (
        "tree",
        capture["tree"],
        capture["stringify"],
        capture["raw"],
        capture["segment_kwargs"],
        capture["has_unparsable"],
        capture["class_types"],
    )


def lex_capture(engine, config, sql):
    """Lex ``sql`` with one lexer (``python``/``rust``); capture the stream.

    Tokens are fingerprinted with their class, raw, type, position marker,
    instance types and all normalization kwargs; lex errors with their type
    and message.
    """
    from sqlfluff.core.parser.lexer import PyLexer, PyRsLexer

    lexer_cls = PyLexer if engine == "python" else PyRsLexer
    tokens, errors = lexer_cls(config=config).lex(sql)

    def token_fingerprint(seg):
        pos = seg.pos_marker
        return (
            type(seg).__name__,
            seg.raw,
            seg.get_type(),
            tuple(sorted(seg.class_types)),
            (
                (pos.source_slice.start, pos.source_slice.stop),
                (pos.templated_slice.start, pos.templated_slice.stop),
                pos.working_line_no,
                pos.working_line_pos,
            )
            if pos
            else None,
            tuple(
                _normalize_kwarg(getattr(seg, attr, None))
                for attr in (
                    "trim_start",
                    "trim_chars",
                    "quoted_value",
                    "escape_replacements",
                    "casefold",
                )
            ),
        )

    return (
        [token_fingerprint(token) for token in tokens],
        [(type(err).__name__, str(err)) for err in errors],
    )


# ---------------------------------------------------------------------------
# RsMatchResult structural invariants.
#
# A malformed match result (out-of-bounds slice, overlapping/unsorted
# children, zero-length node carrying a class or children) is a rust-core bug
# by definition: MatchResult.apply raises its internal "Segment skip ahead"
# ValueError on overlap instead of a parse error, and silent shapes would
# corrupt trees.
# ---------------------------------------------------------------------------


def _match_result_violations(rs_match, n_tokens, path="root"):
    start, stop = rs_match.matched_slice
    if start > stop:
        yield (path, f"inverted slice ({start},{stop})")
    if stop > n_tokens:
        yield (path, f"slice out of bounds ({start},{stop}) n={n_tokens}")
    if start == stop:
        if rs_match.matched_class:
            yield (path, f"zero-length with class {rs_match.matched_class}")
        if rs_match.child_matches:
            yield (path, "zero-length with children")
    prev_end = start
    prev_start = None
    for i, child in enumerate(rs_match.child_matches):
        cs, ce = child.matched_slice
        if cs < start or ce > stop:
            yield (
                f"{path}[{i}]",
                f"child ({cs},{ce}) outside parent ({start},{stop})",
            )
        if prev_start is not None and cs < prev_start:
            yield (f"{path}[{i}]", f"children unsorted ({cs} after {prev_start})")
        if cs < prev_end:
            yield (
                f"{path}[{i}]",
                f"overlap: child starts {cs} before prev end {prev_end}",
            )
        prev_end = max(prev_end, ce)
        prev_start = cs
        yield from _match_result_violations(
            child, n_tokens, f"{path}>{child.matched_class or '?'}[{i}]"
        )
    for idx, _seg_type, _impl in rs_match.insert_segments or []:
        if idx < start or idx > stop:
            yield (path, f"insert @{idx} outside ({start},{stop})")


def raw_match_violations(sql, dialect):
    """Parse SQL to a raw RsMatchResult and list structural violations."""
    from sqlfluff.core.parser import Lexer

    config = build_config(dialect=dialect)
    segments, _ = Lexer(config=config).lex(sql)
    parser = RustParser(config=config)
    start = 0
    for start in range(len(segments)):
        if segments[start].is_code:
            break
    end = len(segments)
    for end in range(len(segments), start - 1, -1):
        if segments[end - 1].is_code:
            break
    if start == end:
        return []
    tokens = parser._extract_tokens_from_segments(segments[start:end])
    try:
        rs_match = parser._rs_parser.parse_match_result_from_tokens(tokens)
    except Exception:
        # Raising a parse error is fine; we only audit *returned* results.
        # Deliberately NOT `except BaseException`: a rust-core panic surfaces
        # as pyo3's PanicException (a BaseException, not an Exception) and is
        # exactly the failure this leg exists to surface, so it must propagate
        # and fail the test rather than be reported as zero violations.
        return []
    return list(_match_result_violations(rs_match, len(tokens)))


# ---------------------------------------------------------------------------
# Fixture-corpus loading (see test/fixtures/parity/README.md for the format).
# ---------------------------------------------------------------------------


def resolve_case_sql(case):
    """Return the case's SQL: inline, or read from the dialect corpus."""
    if "sql" in case:
        return case["sql"]
    return (DIALECT_FIXTURE_DIR / case["sql_fixture"]).read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def _load_case_file(path_str):
    """Parse one parity fixture file, cached by path.

    ``load_case_params`` and ``load_reference_case_params`` each iterate every
    fixture file for every kind, so without a cache the same YAML is re-parsed
    several times per collection. The cached mapping is never mutated below
    (``_meta`` is read, not popped), so the shared object is safe to reuse.
    """
    return yaml.safe_load(Path(path_str).read_text(encoding="utf-8"))


def _iter_case_files(kind):
    for path in sorted(PARITY_CASE_DIR.glob("*.yml")):
        data = _load_case_file(str(path))
        # An empty or comment-only fixture file parses to None (or an empty
        # mapping); skip it rather than crashing collection of the whole suite.
        if not data:
            continue
        meta = data.get("_meta", {})
        if meta.get("kind", "parser") != kind:
            continue
        cases = {name: case for name, case in data.items() if name != "_meta"}
        yield path, cases


def load_case_params(kind, legs):
    """Build pytest params: one per (case, leg), with per-leg strict xfails.

    Every case runs on every leg of its kind. A known divergence is declared
    per-leg in the case's ``xfail`` mapping, which becomes a STRICT xfail:
    the moment the underlying gap is fixed, CI flags the stale marker.

    Every key in a case's ``xfail`` mapping must name a real leg of the case's
    kind. An unknown key (a typo, or a marker scoped to a leg this kind doesn't
    run) is silently ignored by the per-leg lookup below and would leave a known
    divergence unguarded, so it is rejected loudly at collection time instead.
    """
    valid_legs = set(legs)
    params = []
    for path, cases in _iter_case_files(kind):
        for name, case in cases.items():
            unknown = set(case.get("xfail") or {}) - valid_legs
            if unknown:
                raise ValueError(
                    f"{path.name}:{name}: xfail leg(s) {sorted(unknown)} are not "
                    f"valid legs for kind {kind!r} (expected one of {sorted(valid_legs)})"
                )
            for leg in legs:
                marks = []
                reason = (case.get("xfail") or {}).get(leg)
                if reason:
                    marks.append(pytest.mark.xfail(strict=True, reason=reason))
                params.append(
                    pytest.param(case, leg, id=f"{path.stem}:{name}:{leg}", marks=marks)
                )
    return params


def load_reference_case_params(kind):
    """Build pytest params for the reference-expectation sweep.

    One per case that declares an ``expect`` (cases without one have nothing
    to check).

    Unlike ``load_case_params`` these carry no per-leg xfail marks - the
    reference-expectation check runs unconditionally on the pure-Python leg, so
    that a case whose parity comparison is a strict xfail still has its ``expect``
    sanity conditions enforced (under the parity test the comparison assert fails
    first and the strict xfail swallows any later ``expect`` failure).
    """
    params = []
    for path, cases in _iter_case_files(kind):
        for name, case in cases.items():
            if case.get("expect"):
                params.append(pytest.param(case, id=f"{path.stem}:{name}"))
    return params


def reference_capture(case):
    """Capture the pure-Python reference leg for a parser case (templated or not).

    Returns a tuple in the same shape ``check_expectations`` consumes.
    """
    sql = resolve_case_sql(case)
    dialect = case.get("dialect", "ansi")
    if case.get("templater"):
        return _linted_capture_as_tuple(
            linted_parse_capture(
                "python",
                sql,
                dialect=dialect,
                configs=case.get("configs"),
                context=case.get("context"),
            )
        )
    from sqlfluff.core.parser import Lexer

    config = build_config(dialect, case.get("configs"))
    segments, _ = Lexer(config=config).lex(sql)
    return parse_capture("python", config, segments)


def check_expectations(case, reference_capture):
    """Assert the case's ``expect`` sanity conditions on the reference capture.

    Expectations catch a case that quietly stops testing anything real (e.g.
    "parses cleanly on both engines" would also pass if both engines crashed
    the same way). They apply to the reference (pure-Python) leg only.
    """
    expectations = case.get("expect") or []
    if isinstance(expectations, str):
        expectations = [expectations]
    for expectation in expectations:
        if expectation == "tree":
            assert reference_capture[0] == "tree", (
                f"expected a parse tree, got: {reference_capture[:3]}"
            )
        elif expectation == "clean_tree":
            assert reference_capture[0] == "tree", (
                f"expected a parse tree, got: {reference_capture[:3]}"
            )
            assert not reference_capture[5], (
                "expected a clean parse without unparsable segments"
            )
        elif expectation == "error":
            assert reference_capture[0] == "exc", (
                f"expected a raised error, got: {reference_capture[0]}"
            )
        elif expectation == "quoted_kwargs":
            assert reference_capture[0] == "tree" and reference_capture[4], (
                "expected at least one segment carrying normalization kwargs"
            )
        else:
            raise ValueError(f"Unknown expectation: {expectation!r}")
