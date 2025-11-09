"""The Test file for The New Parser (Lexing steps)."""

import logging
from typing import Any, NamedTuple, Union

import pytest

from sqlfluff.core import FluffConfig, SQLLexError
from sqlfluff.core.parser import CodeSegment, Lexer, NewlineSegment, PyLexer
from sqlfluff.core.parser.lexer import LexMatch, RegexLexer, StringLexer
from sqlfluff.core.parser.segments.meta import TemplateSegment
from sqlfluff.core.templaters import (
    JinjaTemplater,
    PlaceholderTemplater,
    RawFileSlice,
    TemplatedFile,
)
from sqlfluff.core.templaters.base import TemplatedFileSlice

try:
    from sqlfluff.core.parser.lexer import PyRsLexer
    from sqlfluffrs import RsSQLLexerError

    SQLLexErrorClass = (SQLLexError, RsSQLLexerError)
    HAS_RUST_LEXER = True
except ImportError:
    PyRsLexer = None  # type: ignore
    SQLLexErrorClass = (SQLLexError,)
    HAS_RUST_LEXER = False


def assert_matches(instring, matcher, matchstring):
    """Assert that a matcher does or doesn't work on a string.

    The optional `matchstring` argument, which can optionally
    be None, allows to either test positive matching of a
    particular string or negative matching (that it explicitly)
    doesn't match.
    """
    res = matcher.match(instring)
    # Check we've got the right type
    assert isinstance(res, LexMatch)
    if matchstring is None:
        assert res.forward_string == instring
        assert res.elements == []
    else:
        assert res.forward_string == instring[len(matchstring) :]
        assert len(res.elements) == 1
        assert res.elements[0].raw == matchstring


@pytest.mark.parametrize(
    "raw,res",
    [
        # NOTE: The final empty string is the end of file marker
        ("a b", ["a", " ", "b", ""]),
        ("b.c", ["b", ".", "c", ""]),
        (
            "abc \n \t def  ;blah",
            ["abc", " ", "\n", " \t ", "def", "  ", ";", "blah", ""],
        ),
        # Test Quotes
        ('abc\'\n "\t\' "de`f"', ["abc", "'\n \"\t'", " ", '"de`f"', ""]),
        # Test Comments
        ("abc -- comment \nblah", ["abc", " ", "-- comment ", "\n", "blah", ""]),
        ("abc # comment \nblah", ["abc", " ", "# comment ", "\n", "blah", ""]),
        # Note the more complicated parsing of block comments.
        # This tests subdivision and trimming (incl the empty case)
        (
            "abc /* comment \nblah*/",
            ["abc", " ", "/* comment", " ", "\n", "blah*/", ""],
        ),
        ("abc /*\n\t\n*/", ["abc", " ", "/*", "\n", "\t", "\n", "*/", ""]),
        # Test strings
        ("*-+bd/", ["*", "-", "+", "bd", "/", ""]),
        # Test Negatives and Minus
        ("2+4 -5", ["2", "+", "4", " ", "-", "5", ""]),
        ("when 'Spec\\'s 23' like", ["when", " ", "'Spec\\'s 23'", " ", "like", ""]),
        ('when "Spec\\"s 23" like', ["when", " ", '"Spec\\"s 23"', " ", "like", ""]),
    ],
)
def test__parser__lexer_obj(raw, res, caplog):
    """Test the lexer splits as expected in a selection of cases."""
    lex = Lexer(config=FluffConfig(overrides={"dialect": "ansi"}))
    with caplog.at_level(logging.DEBUG):
        lexing_segments, _ = lex.lex(raw)
        assert [seg.raw for seg in lexing_segments] == res


@pytest.mark.parametrize(
    "raw,res",
    [
        (".fsaljk", "."),
        ("fsaljk", None),
    ],
)
def test__parser__lexer_string(raw, res):
    """Test the StringLexer."""
    matcher = StringLexer("dot", ".", CodeSegment)
    assert_matches(raw, matcher, res)


@pytest.mark.parametrize(
    "raw,reg,res",
    [
        ("fsaljk", "f", "f"),
        ("fsaljk", r"f", "f"),
        ("fsaljk", r"[fas]*", "fsa"),
        # Matching whitespace segments
        ("   \t   fsaljk", r"[^\S\r\n]*", "   \t   "),
        # Matching whitespace segments (with a newline)
        ("   \t \n  fsaljk", r"[^\S\r\n]*", "   \t "),
        # Matching quotes containing stuff
        ("'something boring'   \t \n  fsaljk", r"'[^']*'", "'something boring'"),
        (
            "' something exciting \t\n '   \t \n  fsaljk",
            r"'[^']*'",
            "' something exciting \t\n '",
        ),
    ],
)
def test__parser__lexer_regex(raw, reg, res, caplog):
    """Test the RegexLexer."""
    matcher = RegexLexer("test", reg, CodeSegment)
    with caplog.at_level(logging.DEBUG):
        assert_matches(raw, matcher, res)


def test__parser__lexer_lex_match(caplog):
    """Test the RepeatedMultiMatcher."""
    matchers = [
        StringLexer("dot", ".", CodeSegment),
        RegexLexer("test", r"#[^#]*#", CodeSegment),
    ]
    with caplog.at_level(logging.DEBUG):
        res = PyLexer.lex_match("..#..#..#", matchers)
        assert res.forward_string == "#"  # Should match right up to the final element
        assert len(res.elements) == 5
        assert res.elements[2].raw == "#..#"


def test__parser__lexer_fail():
    """Test the how the lexer fails and reports errors."""
    lex = Lexer(config=FluffConfig(overrides={"dialect": "ansi"}))

    _, vs = lex.lex("Select \u0394")

    assert len(vs) == 1
    err = vs[0]
    assert isinstance(err, SQLLexErrorClass)
    assert err.line_pos == 8


def test__parser__lexer_fail_via_parse():
    """Test the how the parser fails and reports errors while lexing."""
    lexer = Lexer(config=FluffConfig(overrides={"dialect": "ansi"}))
    _, vs = lexer.lex("Select \u0394")
    assert vs
    assert len(vs) == 1
    err = vs[0]
    assert isinstance(err, SQLLexErrorClass)
    assert err.line_pos == 8


def test__parser__lexer_trim_post_subdivide(caplog):
    """Test a RegexLexer with a trim_post_subdivide function."""
    matcher = [
        RegexLexer(
            "function_script_terminator",
            r";\s+(?!\*)\/(?!\*)|\s+(?!\*)\/(?!\*)",
            CodeSegment,
            segment_kwargs={"type": "function_script_terminator"},
            subdivider=StringLexer(
                "semicolon", ";", CodeSegment, segment_kwargs={"type": "semicolon"}
            ),
            trim_post_subdivide=RegexLexer(
                "newline",
                r"(\n|\r\n)+",
                NewlineSegment,
            ),
        )
    ]
    with caplog.at_level(logging.DEBUG):
        res = PyLexer.lex_match(";\n/\n", matcher)
        assert res.elements[0].raw == ";"
        assert res.elements[1].raw == "\n"
        assert res.elements[2].raw == "/"
        assert len(res.elements) == 3


class _LexerSlicingCase(NamedTuple):
    name: str
    in_str: str
    context: dict[str, Any]
    # (
    #     raw,
    #     source_str (if TemplateSegment),
    #     block_type (if TemplateSegment),
    #     segment_type
    # )
    expected_segments: list[tuple[str, Union[str, None], Union[str, None], str]]


def _statement(*args, **kwargs):
    return ""


def _load_result(*args, **kwargs):
    return ["foo", "bar"]


@pytest.mark.parametrize(
    "case",
    [
        _LexerSlicingCase(
            name="call macro and function overrides",
            in_str="{% call statement('unique_keys', fetch_result=true) %}\n"
            "    select 1 as test\n"
            "{% endcall %}\n"
            "{% set unique_keys = load_result('unique_keys') %}\n"
            "select 2\n",
            context={"statement": _statement, "load_result": _load_result},
            expected_segments=[
                (
                    "",
                    "{% call statement('unique_keys', fetch_result=true) %}",
                    "block_start",
                    "placeholder",
                ),
                ("", None, None, "indent"),
                ("", "\n    select 1 as test\n", "literal", "placeholder"),
                ("", None, None, "dedent"),
                ("", "{% endcall %}", "block_end", "placeholder"),
                ("\n", None, None, "newline"),
                (
                    "",
                    "{% set unique_keys = load_result('unique_keys') %}",
                    "templated",
                    "placeholder",
                ),
                ("\n", None, None, "newline"),
                ("select", None, None, "word"),
                (" ", None, None, "whitespace"),
                ("2", None, None, "literal"),
                ("\n", None, None, "newline"),
                ("", None, None, "end_of_file"),
            ],
        ),
        _LexerSlicingCase(
            name="call an existing macro",
            in_str="{% macro render_name(title) %}\n"
            "  '{{ title }}. foo' as {{ caller() }}\n"
            "{% endmacro %}\n"
            "SELECT\n"
            "    {% call render_name('Sir') %}\n"
            "        bar\n"
            "    {% endcall %}\n"
            "FROM baz\n",
            context={},
            expected_segments=[
                ("", "{% macro render_name(title) %}", "block_start", "placeholder"),
                ("", None, None, "indent"),
                ("", "\n  '", "literal", "placeholder"),
                ("", "{{ title }}", "templated", "placeholder"),
                ("", ". foo' as ", "literal", "placeholder"),
                ("", "{{ caller() }}", "templated", "placeholder"),
                ("", "\n", "literal", "placeholder"),
                ("", None, None, "dedent"),
                ("", "{% endmacro %}", "block_end", "placeholder"),
                ("\n", None, None, "newline"),
                ("SELECT", None, None, "word"),
                ("\n", None, None, "newline"),
                ("    ", None, None, "whitespace"),
                ("\n", None, None, "newline"),
                ("  ", None, None, "whitespace"),
                ("'Sir. foo'", None, None, "raw"),
                (" ", None, None, "whitespace"),
                ("as", None, None, "word"),
                (" ", None, None, "whitespace"),
                ("\n", None, None, "newline"),
                ("        ", None, None, "whitespace"),
                ("bar", None, None, "word"),
                ("\n", None, None, "newline"),
                ("    ", None, None, "whitespace"),
                ("\n", None, None, "newline"),
                ("", "\n        bar\n    ", "literal", "placeholder"),
                ("", None, None, "dedent"),
                ("", "{% endcall %}", "block_end", "placeholder"),
                ("\n", None, None, "newline"),
                ("FROM", None, None, "word"),
                (" ", None, None, "whitespace"),
                ("baz", None, None, "word"),
                ("\n", None, None, "newline"),
                ("", None, None, "end_of_file"),
            ],
        ),
    ],
    ids=lambda case: case.name,
)
def test__parser__lexer_slicing_calls(case: _LexerSlicingCase):
    """Test slicing of call blocks.

    https://github.com/sqlfluff/sqlfluff/issues/4013
    """
    config = FluffConfig(overrides={"dialect": "ansi"})

    templater = JinjaTemplater(override_context=case.context)

    templated_file, templater_violations = templater.process(
        in_str=case.in_str, fname="test.sql", config=config, formatter=None
    )

    assert not templater_violations, (
        f"Found templater violations: {templater_violations}"
    )

    lexer = Lexer(config=config)
    lexing_segments, lexing_violations = lexer.lex(templated_file)

    assert not lexing_violations, f"Found templater violations: {lexing_violations}"
    assert case.expected_segments == [
        (
            seg.raw,
            seg.source_str if isinstance(seg, TemplateSegment) else None,
            seg.block_type if isinstance(seg, TemplateSegment) else None,
            seg.type,
        )
        for seg in lexing_segments
    ]


class _LexerSlicingTemplateFileCase(NamedTuple):
    name: str
    # easy way to build inputs here is to call templater.process in
    # test__parser__lexer_slicing_calls and adjust the output how you like:
    file: TemplatedFile
    # (
    #     raw,
    #     source_str (if TemplateSegment),
    #     block_type (if TemplateSegment),
    #     segment_type
    # )
    expected_segments: list[tuple[str, Union[str, None], Union[str, None], str]]


@pytest.mark.parametrize(
    "case",
    [
        _LexerSlicingTemplateFileCase(
            name="very simple test case",
            file=TemplatedFile(
                source_str="SELECT {# comment #}1;",
                templated_str="SELECT 1;",
                fname="test.sql",
                sliced_file=[
                    TemplatedFileSlice("literal", slice(0, 7, None), slice(0, 7, None)),
                    TemplatedFileSlice(
                        "comment", slice(7, 20, None), slice(7, 7, None)
                    ),
                    TemplatedFileSlice(
                        "literal", slice(20, 22, None), slice(7, 9, None)
                    ),
                ],
                raw_sliced=[
                    RawFileSlice("SELECT ", "literal", 0, 0, None),
                    RawFileSlice("{# comment #}", "comment", 7, 0, None),
                    RawFileSlice("1;", "literal", 20, 0, None),
                ],
            ),
            expected_segments=[
                ("SELECT", None, None, "word"),
                (" ", None, None, "whitespace"),
                ("", "{# comment #}", "comment", "placeholder"),
                ("1", None, None, "literal"),
                (";", None, None, "raw"),
                ("", None, None, "end_of_file"),
            ],
        ),
        _LexerSlicingTemplateFileCase(
            name="special zero length slice type is kept",
            file=TemplatedFile(
                source_str="SELECT 1;",
                templated_str="SELECT 1;",
                fname="test.sql",
                sliced_file=[
                    TemplatedFileSlice("literal", slice(0, 7, None), slice(0, 7, None)),
                    # this is a special marker that the templater wants to show up
                    # as a meta segment:
                    TemplatedFileSlice(
                        "special_type", slice(7, 7, None), slice(7, 7, None)
                    ),
                    TemplatedFileSlice("literal", slice(7, 9, None), slice(7, 9, None)),
                ],
                raw_sliced=[
                    RawFileSlice("SELECT 1;", "literal", 0, 0, None),
                ],
            ),
            expected_segments=[
                ("SELECT", None, None, "word"),
                (" ", None, None, "whitespace"),
                ("", "", "special_type", "placeholder"),
                ("1", None, None, "literal"),
                (";", None, None, "raw"),
                ("", None, None, "end_of_file"),
            ],
        ),
        _LexerSlicingTemplateFileCase(
            name="template with escaped slice",
            file=TemplatedFile(
                source_str="SELECT '{{}}' FROM TAB;",
                templated_str="SELECT '{}' FROM TAB;",
                fname="test.sql",
                sliced_file=[
                    TemplatedFileSlice("literal", slice(0, 8, None), slice(0, 8, None)),
                    TemplatedFileSlice(
                        "escaped", slice(8, 12, None), slice(8, 10, None)
                    ),
                    TemplatedFileSlice(
                        "literal", slice(12, 23, None), slice(10, 21, None)
                    ),
                ],
                raw_sliced=[
                    RawFileSlice("SELECT '", "literal", 0, 0, None),
                    RawFileSlice("{{", "escaped", 8, 0, None),
                    RawFileSlice("}}", "escaped", 10, 0, None),
                    RawFileSlice("' FROM TAB;", "literal", 12, 0, None),
                ],
            ),
            expected_segments=[
                ("SELECT", None, None, "word"),
                (" ", None, None, "whitespace"),
                ("'{}'", None, None, "raw"),
                (" ", None, None, "whitespace"),
                ("FROM", None, None, "word"),
                (" ", None, None, "whitespace"),
                ("TAB", None, None, "word"),
                (";", None, None, "raw"),
                ("", None, None, "end_of_file"),
            ],
        ),
    ],
    ids=lambda case: case.name,
)
def test__parser__lexer_slicing_from_template_file(case: _LexerSlicingTemplateFileCase):
    """Test slicing using a provided TemplateFile.

    Useful for testing special inputs without having to find a templater to trick
    and yield the input you want to test.
    """
    config = FluffConfig(overrides={"dialect": "ansi"})

    lexer = Lexer(config=config)
    lexing_segments, lexing_violations = lexer.lex(case.file)

    assert not lexing_violations, f"Found templater violations: {lexing_violations}"
    assert case.expected_segments == [
        (
            seg.raw,
            seg.source_str if isinstance(seg, TemplateSegment) else None,
            seg.block_type if isinstance(seg, TemplateSegment) else None,
            seg.type,
        )
        for seg in lexing_segments
    ]


@pytest.mark.skipif(not HAS_RUST_LEXER, reason="Rust lexer not available")
def test__parser__pyrs_lexer_tokens_to_segments():
    """Test the _tokens_to_segments static method."""
    from unittest.mock import Mock

    from sqlfluff.core.parser.segments import RawSegment

    # Create a mock templated file
    py_template = TemplatedFile.from_string("SELECT 1")

    # Helper function to create a complete mock token
    def create_mock_token(
        token_type, raw, source_idx, templated_idx, instance_types=None
    ):
        mock_token = Mock()
        mock_token.type = token_type
        mock_token.raw = raw
        mock_token.instance_types = instance_types or [token_type]
        mock_token.trim_start = None
        mock_token.trim_chars = None
        mock_token.source_fixes = None
        mock_token.uuid = None
        mock_token.quoted_value = None
        mock_token.escape_replacements = None

        # Create mock position marker
        mock_pos = Mock()
        mock_pos.source_slice = slice(source_idx, source_idx + len(raw))
        mock_pos.templated_slice = slice(templated_idx, templated_idx + len(raw))
        mock_token.pos_marker = mock_pos
        return mock_token

    # Create mock tokens with different types
    mock_token_word = create_mock_token("word", "SELECT", 0, 0, ["word"])
    mock_token_whitespace = create_mock_token("whitespace", " ", 6, 6, ["whitespace"])
    mock_token_literal = create_mock_token("literal", "1", 7, 7, ["literal"])

    # Test conversion
    tokens = [mock_token_word, mock_token_whitespace, mock_token_literal]
    segments = PyRsLexer._tokens_to_segments(tokens, py_template)

    # Verify results
    assert isinstance(segments, tuple)
    assert len(segments) == 3
    assert all(isinstance(seg, RawSegment) for seg in segments)
    assert segments[0].raw == "SELECT"
    assert segments[1].raw == " "
    assert segments[2].raw == "1"


@pytest.mark.skipif(not HAS_RUST_LEXER, reason="Rust lexer not available")
def test__parser__pyrs_lexer_tokens_to_segments_empty():
    """Test _tokens_to_segments with empty token list."""
    py_template = TemplatedFile.from_string("")

    segments = PyRsLexer._tokens_to_segments([], py_template)

    assert isinstance(segments, tuple)
    assert len(segments) == 0


@pytest.mark.skipif(not HAS_RUST_LEXER, reason="Rust lexer not available")
def test__parser__pyrs_lexer_tokens_to_segments_unknown_type():
    """Test _tokens_to_segments with unknown token type falls back to RawSegment."""
    from unittest.mock import Mock

    from sqlfluff.core.parser.segments import RawSegment

    py_template = TemplatedFile.from_string("???")

    # Create a mock token with an unknown type
    mock_token = Mock()
    mock_token.type = "unknown_type_xyz"
    mock_token.raw = "???"
    mock_token.instance_types = ["unknown_type_xyz"]
    mock_token.trim_start = None
    mock_token.trim_chars = None
    mock_token.source_fixes = None
    mock_token.uuid = None
    mock_token.quoted_value = None
    mock_token.escape_replacements = None

    # Create mock position marker
    mock_pos = Mock()
    mock_pos.source_slice = slice(0, 3)
    mock_pos.templated_slice = slice(0, 3)
    mock_token.pos_marker = mock_pos

    segments = PyRsLexer._tokens_to_segments([mock_token], py_template)

    assert isinstance(segments, tuple)
    assert len(segments) == 1
    assert isinstance(segments[0], RawSegment)
    assert segments[0].raw == "???"


@pytest.mark.skipif(not HAS_RUST_LEXER, reason="Rust lexer not available")
def test__parser__pyrs_lexer_integration():
    """Test that PyRsLexer properly integrates _tokens_to_segments in lex method."""
    config = FluffConfig(overrides={"dialect": "ansi"})
    lexer = PyRsLexer(config=config)

    segments, errors = lexer.lex("SELECT 1")

    # Verify that segments were created properly
    assert len(segments) > 0
    # Should have SELECT, whitespace, 1, and EOF
    assert any(seg.raw == "SELECT" for seg in segments)
    assert any(seg.raw == "1" for seg in segments)


@pytest.mark.skipif(not HAS_RUST_LEXER, reason="Rust lexer not available")
def test__parser__pyrs_lexer_unicode_templated_file():
    """Test that PyRsLexer preserves unicode characters in TemplatedFile round-trip.

    This test ensures that when a TemplatedFile with multi-byte UTF-8 characters
    (like Chinese, Japanese, emoji, etc.) is passed to Rust and back, the strings
    remain intact and are not corrupted.

    Regression test for a bug where byte-based indexing was used instead of
    character-based indexing, causing unicode characters to be corrupted
    (e.g., "法" appearing as "æ³•").
    """
    # Test case with multi-byte UTF-8 characters (Chinese character "法")
    # and a templated section (:c placeholder)
    source_str = "SELECT\n    d, -- 法\n    ':c' AS f"

    # Create config with placeholder templater using colon style
    config = FluffConfig(
        overrides={
            "dialect": "ansi",
            "templater": "placeholder",
        },
        configs={
            "core": {},
            "templater": {
                "placeholder": {
                    "param_style": "colon",
                    "c": "'replaced_value'",
                }
            },
        },
    )

    # Process through templater to get a TemplatedFile with sliced sections
    templater = PlaceholderTemplater(
        override_context={"param_style": "colon", "c": "'replaced_value'"}
    )
    templated_file, templater_violations = templater.process(
        in_str=source_str, fname="test.sql", config=config, formatter=None
    )

    assert not templater_violations, (
        f"Unexpected templater violations: {templater_violations}"
    )

    # Verify the templated file has the expected structure
    # The :c should be replaced with 'replaced_value'
    assert "'replaced_value'" in templated_file.templated_str

    # Lex with PyRsLexer (which passes TemplatedFile to Rust and back)
    lexer = PyRsLexer(config=config)
    segments, errors = lexer.lex(templated_file)

    assert not errors, f"Unexpected lexing errors: {errors}"

    # The critical test: verify that the unicode character is preserved
    # Find the comment segment that should contain "法"
    comment_segments = [seg for seg in segments if seg.type == "comment"]
    assert len(comment_segments) == 1, "Should have exactly one comment segment"

    # The comment should still contain the original Chinese character
    assert "法" in comment_segments[0].raw, (
        f"Unicode character '法' was corrupted in round-trip. "
        f"Got: {comment_segments[0].raw!r}"
    )

    # Also verify the entire source_str is preserved correctly
    # by reconstructing it from the segments
    reconstructed_source = "".join(
        seg.source_str
        if isinstance(seg, TemplateSegment) and seg.source_str
        else seg.raw
        for seg in segments
        if seg.type != "end_of_file"
    )

    # The source should contain the original Chinese character
    assert "法" in reconstructed_source, (
        f"Unicode character '法' was lost in reconstruction. "
        f"Got: {reconstructed_source!r}"
    )


@pytest.mark.skipif(not HAS_RUST_LEXER, reason="Rust lexer not available")
@pytest.mark.parametrize(
    "unicode_char,description",
    [
        ("法", "Chinese character (3-byte UTF-8)"),
        ("🔥", "Emoji (4-byte UTF-8)"),
        ("é", "Latin with accent (2-byte UTF-8)"),
        ("العربية", "Arabic text (multi-byte UTF-8)"),
        ("日本語", "Japanese text (multi-byte UTF-8)"),
    ],
)
def test__parser__pyrs_lexer_unicode_preservation(unicode_char, description):
    """Test PyRsLexer preserves various unicode characters.

    Tests multiple unicode characters with different UTF-8 byte lengths
    to ensure the fix for byte vs. character indexing is robust.
    """
    # Create SQL with unicode character in a comment and a template placeholder
    source_str = f"SELECT d, -- {unicode_char}\n':x' AS col"

    config = FluffConfig(
        overrides={
            "dialect": "ansi",
            "templater": "placeholder",
        },
        configs={
            "core": {},
            "templater": {
                "placeholder": {
                    "param_style": "colon",
                    "x": "'val'",
                }
            },
        },
    )

    templater = PlaceholderTemplater(
        override_context={"param_style": "colon", "x": "'val'"}
    )
    templated_file, _ = templater.process(
        in_str=source_str, fname="test.sql", config=config, formatter=None
    )

    lexer = PyRsLexer(config=config)
    segments, errors = lexer.lex(templated_file)

    assert not errors, f"Lexing errors with {description}: {errors}"

    # Find comment and verify unicode is preserved
    comment_segments = [seg for seg in segments if seg.type == "comment"]
    assert len(comment_segments) == 1
    assert unicode_char in comment_segments[0].raw, (
        f"{description} was corrupted. Expected '{unicode_char}', "
        f"got: {comment_segments[0].raw!r}"
    )
