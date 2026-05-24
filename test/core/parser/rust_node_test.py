"""Tests for Rust RsNode position exposure."""

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.parser.lexer import PyRsLexer

try:
    from sqlfluffrs import RsParser

    _HAS_RUST = True
except ImportError:  # pragma: no cover
    _HAS_RUST = False


def _parse_to_rsnode(sql: str, dialect: str = "ansi"):
    """Parse SQL to an RsNode root and return (node, tokens)."""
    config = FluffConfig.from_root(overrides={"dialect": dialect})
    lexer = PyRsLexer(config=config)
    tokens, _ = lexer._lex(sql)
    parser = RsParser(dialect=dialect)
    match_result = parser.parse_match_result_from_tokens(tokens)
    node = match_result.apply_as_node(tokens, [], [])
    return node, tokens


@pytest.mark.skipif(not _HAS_RUST, reason="Rust parser not available")
def test_rsnode_exposes_position_api_on_root_and_keyword():
    """RsNode should expose pos_marker/get_start_loc/get_end_loc."""
    node, _ = _parse_to_rsnode("SELECT a FROM foo")

    assert hasattr(node, "pos_marker")
    assert hasattr(node, "get_start_loc")
    assert hasattr(node, "get_end_loc")

    root_start = node.get_start_loc()
    root_end = node.get_end_loc()

    assert root_start is not None
    assert root_end is not None
    assert root_start[0] >= 1
    assert root_start[1] >= 1
    assert root_end[0] >= root_start[0]

    # Find first keyword node and assert it also has a real location.
    def iter_nodes(n):
        yield n
        children = n.children()
        if children:
            for c in children:
                yield from iter_nodes(c)

    keyword_nodes = [
        n
        for n in iter_nodes(node)
        if n.segment_type == "keyword" and n.raw.upper() in {"SELECT", "FROM"}
    ]
    assert keyword_nodes, "Expected to find keyword nodes"

    kw = keyword_nodes[0]
    assert kw.pos_marker is not None
    kw_start = kw.get_start_loc()
    kw_end = kw.get_end_loc()
    assert kw_start is not None
    assert kw_end is not None
    assert kw_start[0] >= 1
    assert kw_start[1] >= 1
    assert kw_end[0] >= kw_start[0]


@pytest.mark.skipif(not _HAS_RUST, reason="Rust parser not available")
def test_rsnode_exposes_parity_booleans_and_type_helpers():
    """RsNode should expose key BaseSegment-like helpers for parity."""
    node, _ = _parse_to_rsnode("-- leading comment\nSELECT a FROM foo\n")

    # Root-level helpers.
    assert hasattr(node, "raw_upper")
    assert hasattr(node, "is_whitespace")
    assert hasattr(node, "is_meta")
    assert hasattr(node, "is_comment")
    assert hasattr(node, "is_raw")
    assert hasattr(node, "get_type")
    assert hasattr(node, "is_type")

    assert node.raw_upper == node.raw.upper()
    assert node.get_type() == "file"
    assert node.is_type("file")
    assert not node.is_type("keyword")

    def iter_nodes(n):
        yield n
        children = n.children()
        if children:
            for c in children:
                yield from iter_nodes(c)

    all_nodes = list(iter_nodes(node))

    # Keyword parity checks.
    keywords = [n for n in all_nodes if n.segment_type == "keyword"]
    assert keywords, "Expected keyword nodes"
    kw = keywords[0]
    assert kw.is_type("keyword")
    assert kw.get_type() == "keyword"
    assert kw.is_code()
    assert not kw.is_whitespace()
    assert not kw.is_comment()

    # Whitespace parity checks.
    whitespaces = [n for n in all_nodes if n.is_whitespace()]
    assert whitespaces, "Expected whitespace nodes"
    ws = whitespaces[0]
    assert ws.is_whitespace()
    assert not ws.is_code()

    # Comment parity checks.
    comments = [n for n in all_nodes if n.is_comment()]
    assert comments, "Expected comment nodes"
    c = comments[0]
    assert c.is_comment()
    assert not c.is_code()

    # Meta parity checks.
    metas = [n for n in all_nodes if n.is_meta()]
    assert metas, "Expected meta nodes"
    m = metas[0]
    assert m.is_meta()
    assert not m.is_code()

    # Raw-ness checks.
    assert kw.is_raw(), "Keyword should be represented as raw node"
    assert not node.is_raw(), "Root file node should not be raw"
