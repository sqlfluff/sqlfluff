"""Tests for generating Rust lexer matchers."""

import pytest

from sqlfluff.core.parser import CodeSegment
from sqlfluff.core.parser.lexer import StringLexer
from utils.build_lexers import _as_rust_lexer_matcher


@pytest.mark.parametrize(
    "template, literal",
    [
        (".", '"."'),
        (r"\.", r'"\\."'),
        ("\\", r'"\\"'),
        ('"', r'"\""'),
        (r"\n", r'"\\n"'),
        ("\n\r\t", r'"\u{a}\u{d}\u{9}"'),
        ("\r\n", r'"\u{d}\u{a}"'),
        ("\\\n  x", r'"\\\u{a}  x"'),
        ("\0\x08\x0b\x0c\x1b\x1f\x7f", r'"\u{0}\u{8}\u{b}\u{c}\u{1b}\u{1f}\u{7f}"'),
        ('"# "## "###', r'"\"# \"## \"###"'),
        ("é雪😀", '"é雪😀"'),
    ],
)
def test_string_lexer_rust_template(template: str, literal: str) -> None:
    """String templates retain their contents in valid Rust string literals."""
    matcher = StringLexer("test", template, CodeSegment)
    generated = _as_rust_lexer_matcher(matcher, "Ansi")
    assert f"\n        {literal},Token::code_token," in generated
