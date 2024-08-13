"""Tests for use cases of the public api classes."""

from sqlfluff.core import Lexer, Linter, Parser

test_query = "SELECt 1"


def test__api__lexer():
    """Basic checking of lexing functionality."""
    tokens, violations = Lexer(dialect="ansi").lex(test_query)
    assert violations == []
    assert isinstance(tokens, tuple)
    # The last element is the file end marker.
    assert [elem.raw for elem in tokens] == ["SELECt", " ", "1", ""]


def test__api__parser():
    """Basic checking of parsing functionality."""
    tokens, _ = Lexer(dialect="ansi").lex(test_query)
    parsed = Parser(dialect="ansi").parse(tokens)
    assert parsed.raw == test_query


def test__api__linter_lint():
    """Basic checking of parsing functionality."""
    tokens, _ = Lexer(dialect="ansi").lex(test_query)
    parsed = Parser(dialect="ansi").parse(tokens)
    violations = Linter(dialect="ansi").lint(parsed)
    assert [v.rule.code for v in violations] == ["CP01", "LT12"]


def test__api__linter_fix():
    """Basic checking of parsing functionality."""
    tokens, _ = Lexer(dialect="ansi").lex(test_query)
    parsed = Parser(dialect="ansi").parse(tokens)
    fixed, _ = Linter(dialect="ansi").fix(parsed)
    assert fixed.raw == "SELECT 1\n"
