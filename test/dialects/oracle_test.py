"""Oracle dialect specific parser rejection tests.

Verifies that duplicate attributes and mutually-exclusive pairs in Oracle
physical-attribute segments are rejected at parse time (AnySetOf semantics).

Positive/valid-SQL cases belong in the SQL/YAML parse fixtures under
test/fixtures/dialects/oracle/ per project convention.
"""

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.segments import (
    CodeSegment,
    EndOfFile,
    Indent,
    NewlineSegment,
    WhitespaceSegment,
)
from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.dialects.dialect_oracle import _StandaloneSlashTerminator


def _violations(sql: str) -> list:
    """Return all parse errors, including unparsable nodes anywhere in the tree.

    Top-level parse failures surface in parsed.violations, but content that
    cannot be matched inside a Bracketed clause is silently wrapped in an
    unparsable tree node without raising a SQLParseError. We collect both so
    that rejection tests for STORAGE(...) sub-parameters work correctly.
    """
    parsed = Linter(dialect="oracle").parse_string(sql)
    violations: list = list(parsed.violations)
    if parsed.tree:
        violations += list(parsed.tree.recursive_crawl("unparsable"))
    return violations


# OraclePhysicalAttributesSegment - table-level attributes
@pytest.mark.parametrize(
    "sql",
    [
        # Duplicate scalar attributes
        pytest.param(
            "CREATE TABLE t (c NUMBER) PCTFREE 10 PCTFREE 20;",
            id="dup_pctfree",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) PCTUSED 40 PCTUSED 60;",
            id="dup_pctused",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) INITRANS 2 INITRANS 4;",
            id="dup_initrans",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) MAXTRANS 255 MAXTRANS 100;",
            id="dup_maxtrans",
        ),
        # Mutually exclusive pairs
        pytest.param(
            "CREATE TABLE t (c NUMBER) LOGGING NOLOGGING;",
            id="logging_nologging",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) MONITORING NOMONITORING;",
            id="monitoring_nomonitoring",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) ROWDEPENDENCIES NOROWDEPENDENCIES;",
            id="rowdep_norowdep",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) CACHE NOCACHE;",
            id="cache_nocache",
        ),
    ],
)
def test_table_physical_attrs_rejected(sql: str) -> None:
    """Duplicate or mutually-exclusive table physical attributes must produce a parse violation."""
    assert _violations(sql) != [], f"Expected violations but got none for:\n{sql}"


# StorageClauseSegment - STORAGE(...) sub-parameters
@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "CREATE TABLE t (c NUMBER) STORAGE (INITIAL 256K INITIAL 512K);",
            id="storage_dup_initial",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) STORAGE (NEXT 64K NEXT 128K);",
            id="storage_dup_next",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) STORAGE (MAXEXTENTS 100 MAXEXTENTS 200);",
            id="storage_dup_maxextents",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) STORAGE (PCTINCREASE 0 PCTINCREASE 10);",
            id="storage_dup_pctincrease",
        ),
        pytest.param(
            "CREATE TABLE t (c NUMBER) STORAGE (BUFFER_POOL DEFAULT BUFFER_POOL KEEP);",
            id="storage_dup_buffer_pool",
        ),
    ],
)
def test_storage_clause_rejected(sql: str) -> None:
    """Duplicate STORAGE sub-parameters must produce a parse violation."""
    assert _violations(sql) != [], f"Expected violations but got none for:\n{sql}"


# INMEMORY subclause AnySetOf enforcement
@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "CREATE TABLE t (c NUMBER) INMEMORY PRIORITY LOW PRIORITY HIGH;",
            id="inmemory_dup_priority",
        ),
    ],
)
def test_inmemory_subclauses_rejected(sql: str) -> None:
    """Duplicate INMEMORY subclauses must produce a parse violation."""
    assert _violations(sql) != [], f"Expected violations but got none for:\n{sql}"


# OracleIndexPhysicalAttributesSegment - index-level attributes
@pytest.mark.parametrize(
    "sql",
    [
        # Duplicate scalar attributes
        pytest.param(
            "CREATE INDEX i ON t (c) PCTFREE 10 PCTFREE 20;",
            id="index_dup_pctfree",
        ),
        # Mutually exclusive pairs
        pytest.param(
            "CREATE INDEX i ON t (c) LOGGING NOLOGGING;",
            id="index_logging_nologging",
        ),
        pytest.param(
            "CREATE INDEX i ON t (c) NOSORT REVERSE;",
            id="index_nosort_reverse",
        ),
        pytest.param(
            "CREATE INDEX i ON t (c) VISIBLE INVISIBLE;",
            id="index_visible_invisible",
        ),
    ],
)
def test_index_physical_attrs_rejected(sql: str) -> None:
    """Duplicate or mutually-exclusive index physical attributes must produce a parse violation."""
    assert _violations(sql) != [], f"Expected violations but got none for:\n{sql}"


# _StandaloneSlashTerminator: unit tests for the Oracle SQL*Plus slash-buffer
# terminator used by CREATE VIEW ... AS SELECT. The parse_suite fixtures cover
# the ``\n/\n`` (match) and ``expr / expr`` (skip via backward-walk) cases via
# create_view.sql, but the forward-walk branches (whitespace after slash,
# end_of_file meta, non-EOF meta, and non-newline continuation-line division)
# only fire under the Python parser and are only naturally exercised by the
# ``\n / y`` continuation-line case, so we exercise them here directly.


def _segments(*elems):
    r"""Build a segment list for terminator tests.

    Recognises ``"\n"`` as a NewlineSegment, blank/space-only strings as
    WhitespaceSegments, ``"<eof>"`` as an EndOfFile meta, and ``"<indent>"``
    as an Indent meta (a non-EOF meta). Everything else becomes a CodeSegment.
    """
    raw = "".join(e for e in elems if e not in ("<eof>", "<indent>"))
    tf = TemplatedFile.from_string(raw or " ")
    out = []
    idx = 0
    for elem in elems:
        if elem == "<eof>":
            out.append(EndOfFile(pos_marker=PositionMarker.from_point(idx, idx, tf)))
            continue
        if elem == "<indent>":
            out.append(Indent(pos_marker=PositionMarker.from_point(idx, idx, tf)))
            continue
        if elem == "\n":
            cls = NewlineSegment
        elif set(elem) <= {" ", "\t"}:
            cls = WhitespaceSegment
        else:
            cls = CodeSegment
        out.append(
            cls(
                raw=elem,
                pos_marker=PositionMarker(
                    slice(idx, idx + len(elem)),
                    slice(idx, idx + len(elem)),
                    tf,
                ),
            )
        )
        idx += len(elem)
    return out


def test_standalone_slash_terminator_is_optional_and_cache_key() -> None:
    """Trivial accessors used by the parser framework's caching machinery."""
    t = _StandaloneSlashTerminator()
    assert t.is_optional() is False
    assert t.cache_key() == "oracle-standalone-slash-terminator"
    # ``simple`` returns the fast-match hint the parser uses to skip ahead.
    literals, types = t.simple(parse_context=None)
    assert "/" in literals
    assert types == frozenset()


def test_standalone_slash_terminator_matches_slash_at_start_of_stream() -> None:
    """A leading `/` followed by a newline still matches (backward walk hits SOI)."""
    segs = _segments("/", "\n")
    result = _StandaloneSlashTerminator().match(segs, 0, parse_context=None)
    assert result.matched_slice == slice(0, 1)


def test_standalone_slash_terminator_matches_with_trailing_whitespace() -> None:
    """Whitespace between the slash and the terminating newline is skipped."""
    segs = _segments("\n", "/", " ", "\n")
    result = _StandaloneSlashTerminator().match(segs, 1, parse_context=None)
    assert result.matched_slice == slice(1, 2)


def test_standalone_slash_terminator_matches_at_end_of_file_meta() -> None:
    """A bare `/` immediately before an EndOfFile meta is a valid batch delimiter."""
    segs = _segments("\n", "/", "<eof>")
    result = _StandaloneSlashTerminator().match(segs, 1, parse_context=None)
    assert result.matched_slice == slice(1, 2)


def test_standalone_slash_terminator_skips_non_eof_meta() -> None:
    """A non-EndOfFile meta between the slash and a newline is skipped."""
    segs = _segments("\n", "/", "<indent>", "\n")
    result = _StandaloneSlashTerminator().match(segs, 1, parse_context=None)
    assert result.matched_slice == slice(1, 2)


def test_standalone_slash_terminator_rejects_continuation_line_division() -> None:
    r"""Continuation-line division (`\n / y`) must NOT match as a terminator."""
    segs = _segments("\n", "/", " ", "1024")
    result = _StandaloneSlashTerminator().match(segs, 1, parse_context=None)
    assert result.matched_slice == slice(1, 1)  # empty match => not a terminator


def test_standalone_slash_terminator_rejects_slash_after_expression() -> None:
    """Same-line `expr / expr` division: backward walk hits code, rejects."""
    segs = _segments("1", " ", "/", " ", "100")
    result = _StandaloneSlashTerminator().match(segs, 2, parse_context=None)
    assert result.matched_slice == slice(2, 2)  # empty match


def test_standalone_slash_terminator_rejects_non_slash_at_idx() -> None:
    """Guard: match() bails gracefully at a non-slash position or past EOS."""
    t = _StandaloneSlashTerminator()
    segs = _segments("x")
    assert t.match(segs, 0, parse_context=None).matched_slice == slice(0, 0)
    assert t.match(segs, 5, parse_context=None).matched_slice == slice(5, 5)
