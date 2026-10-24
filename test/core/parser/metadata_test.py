"""Accepted match metadata must support optional grammar inserts immutably."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import BaseSegment, Dedent, ImplicitIndent, Indent, Lexer
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.metadata import match_bounds, match_class_name
from sqlfluff.core.parser.parser import Parser


class ParentSegment(BaseSegment):
    """A container used to check metadata selection independently of SQL."""

    type = "parent"


class ChildSegment(BaseSegment):
    """A matched child with a distinct class name."""

    type = "child"


def test_parse_context_metadata_without_dialect():
    """A dialect-free context retains the generic indentation configuration."""
    config = FluffConfig(
        require_dialect=False, configs={"indentation": {"indented_joins": True}}
    )
    context = ParseContext.from_config(config)
    assert context.dialect is None
    assert context.indentation_config["indented_joins"] is True


def test_parser_preserves_existing_root_parse_extension_signature(monkeypatch):
    """A custom file root can keep the existing root_parse entry point."""
    config = FluffConfig(overrides={"dialect": "ansi", "use_rust_parser": False})
    parser = Parser(config=config)

    class CustomFileSegment(parser.RootSegment):
        """A dialect extension implementing the original root parse signature."""

        @classmethod
        def root_parse(cls, segments, parse_context, fname=None):
            return super().root_parse(segments, parse_context, fname=fname)

    monkeypatch.setattr(parser, "RootSegment", CustomFileSegment)
    sql = "SELECT foo;\n"
    tokens, errors = Lexer(config=config).lex(sql)
    assert not errors
    tree = parser.parse(tokens, fname="custom-root.sql")
    assert isinstance(tree, CustomFileSegment)
    assert tree.raw == sql
    assert tree.file_path == "custom-root.sql"
    assert not list(tree.iter_unparsables())


def test_match_metadata_filters_only_selected_inserts():
    """Filtering must retain unrelated markers, children and the cached original."""
    child = MatchResult(slice(0, 1), matched_class=ChildSegment)
    match = MatchResult(
        slice(0, 2),
        matched_class=ParentSegment,
        child_matches=(child,),
        insert_segments=((0, ImplicitIndent), (0, Indent), (0, Indent), (2, Dedent)),
    )
    assert match.matches_with_child_class("ChildSegment") == [match]
    assert not match.matches_with_child_class("MissingSegment")
    assert match.without_meta_inserts({}) is match
    filtered = match.without_meta_inserts(
        {("ParentSegment", 0, 2): ((0, "Indent"), (2, "Dedent"))}
    )
    assert filtered.insert_segments == ((0, ImplicitIndent), (0, Indent))
    assert filtered.child_matches[0] is child
    assert len(match.insert_segments) == 4
    assert match.without_meta_inserts({("Other", 0, 2): ((0, "Indent"),)}) is match


def test_match_metadata_traversal_does_not_add_recursion_limits():
    """Deep accepted matches can be queried and filtered without recursive copies."""
    match = MatchResult(
        slice(0, 1), matched_class=ChildSegment, insert_segments=((0, Indent),)
    )
    for _ in range(1500):
        match = MatchResult(
            slice(0, 1), matched_class=ParentSegment, child_matches=(match,)
        )
    assert len(match.matches_with_child_class("ChildSegment")) == 1
    filtered = match.without_meta_inserts({("ChildSegment", 0, 1): ((0, "Indent"),)})
    for _ in range(1500):
        filtered = filtered.child_matches[0]
    assert not filtered.insert_segments


@pytest.mark.parametrize(
    "cls,expected",
    [(None, ""), (ParentSegment, "ParentSegment"), ("ParentSegment", "ParentSegment")],
)
@pytest.mark.parametrize("span", [slice(2, 5), (2, 5)])
def test_match_metadata_reads_both_backend_shapes(cls, expected, span):
    """Native names/tuples and Python classes/slices expose the same metadata."""
    match = SimpleNamespace(matched_class=cls, matched_slice=span)
    assert match_class_name(match) == expected
    assert match_bounds(match) == (2, 5)


@pytest.mark.parametrize("backend", ["python", "native", "legacy"])
@pytest.mark.parametrize(
    "style,sql",
    [
        ("indented", "SELECT (foo).LOWER().TRIM();"),
        ("consistent", "    SELECT (foo)\n    .LOWER().TRIM();"),
        ("consistent", "\n\n    SELECT (foo)\n        .LOWER().TRIM();"),
        ("consistent", "SELECT ((foo)\n    .LOWER()).TRIM();"),
    ],
)
def test_parser_grammar_metadata_backend_parity(backend, style, sql, monkeypatch):
    """Both native AST paths and the arena must see the same filtered grammar."""
    config = FluffConfig(
        overrides={"dialect": "bigquery", "use_rust_parser": False},
        configs={"rules": {"bigquery.chained_functions": {"writing_style": style}}},
    )
    tokens, errors = Lexer(config=config).lex(sql)
    assert not errors
    expected = Parser(config=config).parse(tokens)
    assert expected is not None and not list(expected.iter_unparsables())
    if backend == "python":
        tree = expected
    else:
        from sqlfluff.core.parser import rust_parser

        if rust_parser.RustParser is None:
            pytest.skip("sqlfluffrs unavailable")
        config.set_value(("core", "use_rust_parser"), True)
        monkeypatch.setattr(rust_parser, "_NATIVE_AST_ENABLED", backend == "native")
        tokens, errors = Lexer(config=config).lex(sql)
        assert not errors
        tree = rust_parser.RustParser(config=config).parse(tokens)
        assert tree is not None
        assert tree.to_tuple(show_raw=True, include_meta=True) == expected.to_tuple(
            show_raw=True, include_meta=True
        )
        assert tree._rs_tree is not None
        assert [(raw.type, raw.raw) for raw in tree._rs_tree.root.raw_segments()] == [
            (raw.get_type(), raw.raw) for raw in tree.raw_segments
        ]
    assert tree.raw == sql
    assert config.get("indented_chained_functions", ["indentation"]) is None


def test_consistent_grammar_metadata_does_not_leak_between_files():
    """Reusing one parser must resolve each accepted file independently."""
    config = FluffConfig(overrides={"dialect": "bigquery"})
    parser = Parser(config=config)
    indented = "SELECT\n    (foo)\n        .LOWER();\n"
    aligned = "SELECT\n    (foo)\n    .LOWER();\n"
    counts = []
    for sql in (indented, aligned, indented):
        tokens, errors = Lexer(config=config).lex(sql)
        assert not errors
        tree = parser.parse(tokens)
        assert tree is not None
        counts.append(sum(raw.is_type("indent") for raw in tree.raw_segments))
    assert counts[0] == counts[2] == counts[1] + 2
    assert not Linter(config=config).parse_string(indented).violations


@pytest.mark.parametrize(
    "sql,indented",
    [
        ("    SELECT (foo)\n    .LOWER().TRIM();", False),
        ("\n\n    SELECT (foo)\n        .LOWER().TRIM();", True),
        ("SELECT ((foo)\n    .LOWER()).TRIM();", True),
        ("SELECT ((foo).LOWER())\n    .TRIM();", False),
    ],
)
def test_consistent_metadata_uses_one_match_and_native_token_offsets(
    sql, indented, monkeypatch
):
    """Inference must survive native coordinates without a second grammar pass."""
    config = FluffConfig(overrides={"dialect": "bigquery", "use_rust_parser": False})
    parser = Parser(config=config)
    grammar = parser.RootSegment.match_grammar
    original_match = grammar.match
    accepted = []

    def record_match(*args, **kwargs):
        result = original_match(*args, **kwargs)
        accepted.append(result)
        return result

    matching = Mock(side_effect=record_match)
    monkeypatch.setattr(grammar, "match", matching)
    tokens, errors = Lexer(config=config).lex(sql)
    assert not errors
    tree = parser.parse(tokens)
    assert tree is not None and not list(tree.iter_unparsables())
    matching.assert_called_once()
    match = accepted[0]
    offset = next(index for index, token in enumerate(tokens) if token.is_code)

    def native_view(node):
        """Expose accepted metadata as native class names and local token spans."""
        return SimpleNamespace(
            matched_class=match_class_name(node) or None,
            matched_slice=tuple(index - offset for index in match_bounds(node)),
            child_matches=tuple(native_view(child) for child in node.child_matches),
        )

    native = native_view(match)
    native.matches_with_child_class = lambda name: [
        native_view(parent) for parent in match.matches_with_child_class(name)
    ]
    policy = parser.RootSegment.get_meta_exclusions
    python_exclusions = policy(match, tokens, config)
    native_exclusions = policy(native, tokens, config, offset=offset)
    assert bool(python_exclusions) is not indented
    assert {
        (name, start + offset, stop + offset): tuple(
            (index + offset, cls) for index, cls in inserts
        )
        for (name, start, stop), inserts in native_exclusions.items()
    } == python_exclusions
