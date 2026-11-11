"""Parity of the ``RsSegment`` arena facade against native ``BaseSegment``."""

from collections import defaultdict

import pytest

from sqlfluff.core import FluffConfig, Linter
from test.conftest import config_overrides_for_fixture, get_parse_fixtures, load_file

try:
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
    from sqlfluff.core.parser.segments.rs_segment import RsSegment
except ImportError:  # pragma: no cover
    _HAS_RUST_PARSER = False

parse_success_examples, _ = get_parse_fixtures()


# The parser only builds the arena when Rust rules are on.
_RUST = {"use_rust_parser": True, "use_rust_rules": True}


def _parse(sql, **overrides):
    config = FluffConfig(overrides={**_RUST, "templater": "raw", **overrides})
    # Through the Linter so the MySQL/MariaDB `DELIMITER`/`source` pre-pass runs.
    return Linter(config=config).parse_string(sql).tree


def _pos(pm):
    return (pm.source_slice, pm.templated_slice, pm.working_loc, pm.is_literal())


def _path(steps):
    return [(s.segment.get_type(), s.idx, s.len, s.code_idxs) for s in steps]


def _equal_groups(nodes):
    """Group node indices by `==`, within `hash` buckets as sets and dicts do."""
    buckets = defaultdict(list)
    for idx, node in enumerate(nodes):
        buckets[hash(node)].append(idx)
    return {
        tuple(j for j in idxs if nodes[j] == nodes[i])
        for idxs in buckets.values()
        for i in idxs
    }


def _assert_node_parity(rs, native, path="root"):
    """Assert ``rs`` matches ``native``, then recurse into children in order."""
    here = f"{path}/{native.get_type()}"
    assert (rs.type, rs.get_type()) == (native.type, native.get_type()), here
    assert rs.class_types == native.class_types, here
    assert rs.is_type(native.type) and not rs.is_type("not_a_type"), here
    assert (rs.raw, rs.raw_upper) == (native.raw, native.raw_upper), here
    flags = ("is_code", "is_whitespace", "is_comment", "is_meta", "is_templated")
    assert [getattr(rs, f) for f in flags] == [getattr(native, f) for f in flags]
    assert rs.can_start_end_non_code == native.can_start_end_non_code, here
    assert _pos(rs.pos_marker) == _pos(native.pos_marker), here
    assert rs.get_end_loc() == native.get_end_loc(), here
    assert rs.descendant_type_set == native.descendant_type_set, here
    assert rs.direct_descendant_type_set == native.direct_descendant_type_set
    assert rs._code_indices == native._code_indices, here
    assert rs.source_fixes == native.source_fixes == [], here
    for casefold in (True, False):
        assert rs.raw_normalized(casefold) == native.raw_normalized(casefold), here

    assert rs.is_raw() == native.is_raw(), here
    if native.is_raw():
        assert rs.instance_types == native.instance_types, here
        assert rs.normalize() == native.normalize(), here
        # Rules also pass in a value (RF01 normalises reference parts).
        value = native.raw_upper
        assert rs.normalize(value) == native.normalize(value), here
        assert rs.raw_trimmed() == native.raw_trimmed(), here
    if native.is_meta:
        assert rs.indent_val == native.indent_val, here
        assert rs.is_implicit == native.is_implicit, here
        assert rs.block_type == getattr(native, "block_type", None), here
        uuid = getattr(native, "block_uuid", None)
        assert rs.block_uuid == (uuid.int if uuid else None), here

    assert len(rs.segments) == len(native.segments), here
    for idx, (rs_child, native_child) in enumerate(zip(rs.segments, native.segments)):
        assert rs_child.get_parent() == (rs, idx), here
        _assert_node_parity(rs_child, native_child, here)


@pytest.mark.integration
@pytest.mark.parse_suite
@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize("dialect,file", parse_success_examples)
def test__rs_segment__dialect_fixture_parity(dialect, file):
    """Every arena node matches its native segment over the dialect fixtures."""
    tree = _parse(
        load_file(dialect, file), **config_overrides_for_fixture(dialect, file)
    )
    if getattr(tree, "_rs_tree", None) is None:
        # Only a file with no code (empty, comments only) has no arena.
        assert not tree.is_code, "Rust parser built no arena"
        pytest.skip("no code, so no arena")
    root = RsSegment(tree._rs_tree.root)
    _assert_node_parity(root, tree)
    assert [s.raw for s in root.raw_segments] == [s.raw for s in tree.raw_segments]
    assert root.count_segments() == tree.count_segments()
    assert root.count_segments(raw_only=True) == tree.count_segments(raw_only=True)
    for rs_leaf, leaf in zip(root.raw_segments, tree.raw_segments):
        assert _path(root.path_to(rs_leaf)) == _path(tree.path_to(leaf)), leaf
    # Distinct nodes can be equal natively (same class, raw and start).
    rs_nodes, nodes = list(root.recursive_crawl_all()), list(tree.recursive_crawl_all())
    assert _equal_groups(rs_nodes) == _equal_groups(nodes)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rs_segment__navigation_matches_native():
    """Navigation and crawl helpers return the same nodes as native."""
    sql = "SELECT a AS b, 'it''s' FROM (SELECT c FROM d) AS e\n"
    tree = _parse(sql, dialect="ansi")
    root = RsSegment(tree._rs_tree.root)

    def same(rs_segs, native_segs):
        rs_segs, native_segs = list(rs_segs), list(native_segs)
        assert [(s.get_type(), s.raw) for s in rs_segs] == [
            (s.get_type(), s.raw) for s in native_segs
        ]
        assert [_pos(s.pos_marker) for s in rs_segs] == [
            _pos(s.pos_marker) for s in native_segs
        ]

    same(root.recursive_crawl_all(), tree.recursive_crawl_all())
    same(root.recursive_crawl_all(reverse=True), tree.recursive_crawl_all(True))
    for kwargs in ({}, {"no_recursive_seg_type": "from_clause"}):
        same(
            root.recursive_crawl("select_statement", "identifier", **kwargs),
            tree.recursive_crawl("select_statement", "identifier", **kwargs),
        )
    same(
        root.recursive_crawl("select_statement", recurse_into=False, allow_self=False),
        tree.recursive_crawl("select_statement", recurse_into=False, allow_self=False),
    )
    same(root.get_raw_segments(), tree.get_raw_segments())

    rs_select = next(root.recursive_crawl("select_clause"))
    select = next(tree.recursive_crawl("select_clause"))
    assert rs_select.get_start_loc() == select.get_start_loc()
    same(
        rs_select.get_children("select_clause_element"),
        select.get_children("select_clause_element"),
    )
    same([rs_select.get_child("keyword")], [select.get_child("keyword")])
    assert rs_select.get_child("not_a_type") is select.get_child("not_a_type") is None
    same(rs_select.iter_segments(), select.iter_segments())

    rs_stmt = next(root.recursive_crawl("select_statement"))
    stmt = next(tree.recursive_crawl("select_statement"))
    for kw in (
        {"expanding": ["from_clause"]},
        {"expanding": ["from_clause"], "pass_through": True},
    ):
        same(rs_stmt.iter_segments(**kw), stmt.iter_segments(**kw))

    kids, rs_kids = select.segments, rs_select.segments
    same(
        rs_select.select_children(
            start_seg=rs_kids[0], stop_seg=rs_kids[-1], select_if=lambda s: s.is_code
        ),
        select.select_children(
            start_seg=kids[0], stop_seg=kids[-1], select_if=lambda s: s.is_code
        ),
    )
    same(
        rs_select.select_children(loop_while=lambda s: not s.is_type("comma")),
        select.select_children(loop_while=lambda s: not s.is_type("comma")),
    )

    # One wrapper per node.
    assert RsSegment(tree._rs_tree.root) is root
    # Same list each time, as native: reflow caches on its identity.
    assert root.raw_segments is root.raw_segments
    assert root == root and root != tree
    assert root.uuid == tree._rs_tree.root.uuid
    assert root.get_parent() is None
    assert "select_statement" in repr(rs_stmt)
    assert rs_stmt.source_str == stmt.pos_marker.source_str()

    # No path to self, to a node outside the subtree, or to a non-arena segment.
    assert root.path_to(root) == []
    assert rs_select.path_to(root) == select.path_to(tree) == []
    assert root.path_to(stmt) == []
    # Steps hold the same interned wrappers, top-down from the root.
    steps = root.path_to(rs_select)
    assert steps[0].segment is root and steps[-1].segment is rs_select.get_parent()[0]

    with pytest.raises(AttributeError, match="does not implement 'match_grammar'"):
        root.match_grammar


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rs_segment__cp01_crawl_matches_native():
    """CP01's crawler visits the same nodes over the facade as natively.

    sparksql `DIV` is a raw class with its own grammar; an arena that wraps it
    as `binary_operator > keyword` would have CP01 visit it twice.
    """
    from sqlfluff.core.rules import RuleContext

    config = FluffConfig(overrides={"dialect": "sparksql", "rules": "CP01", **_RUST})
    linter = Linter(config=config)
    tree = linter.parse_string("select 3 div 2, a DIV b from t;\n").tree
    (rule,) = linter.get_rulepack().rules

    def visits(root):
        context = RuleContext(
            dialect=config.get("dialect_obj"),
            fix=False,
            templated_file=None,
            path=None,
            config=config,
            segment=root,
        )
        return [
            (c.segment.get_type(), c.segment.raw, c.segment_idx, len(c.parent_stack))
            for c in rule.crawl_behaviour.crawl(context)
        ]

    native = visits(tree)
    assert [(t, raw) for t, raw, *_ in native if raw.upper() == "DIV"] == [
        ("binary_operator", "div"),
        ("binary_operator", "DIV"),
    ]
    assert visits(RsSegment(tree._rs_tree.root)) == native
