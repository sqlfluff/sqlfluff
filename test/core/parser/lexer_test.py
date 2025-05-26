"""The Test file for The New Parser (Lexing steps)."""

import logging
from typing import Any, NamedTuple, Union

import pytest

from sqlfluff.core import FluffConfig, SQLLexError
from sqlfluff.core.parser import CodeSegment, Lexer, NewlineSegment, PyLexer
from sqlfluff.core.parser.lexer import LexMatch, RegexLexer, StringLexer
from sqlfluff.core.parser.segments.meta import TemplateSegment
from sqlfluff.core.templaters import JinjaTemplater, RawFileSlice, TemplatedFile
from sqlfluff.core.templaters.base import TemplatedFileSlice


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
    lex = Lexer.build(config=FluffConfig(overrides={"dialect": "ansi"}))
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
    lex = Lexer.build(config=FluffConfig(overrides={"dialect": "ansi"}))

    _, vs = lex.lex("Select \u0394")

    assert len(vs) == 1
    err = vs[0]
    assert isinstance(err, SQLLexError)
    assert err.line_pos == 8


def test__parser__lexer_fail_via_parse():
    """Test the how the parser fails and reports errors while lexing."""
    lexer = Lexer.build(config=FluffConfig(overrides={"dialect": "ansi"}))
    _, vs = lexer.lex("Select \u0394")
    assert vs
    assert len(vs) == 1
    err = vs[0]
    assert isinstance(err, SQLLexError)
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

    assert (
        not templater_violations
    ), f"Found templater violations: {templater_violations}"

    lexer = Lexer.build(config=config)
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

    lexer = Lexer.build(config=config)
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
