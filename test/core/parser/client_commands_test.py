"""Tests for lexing scripts run through a command-line client.

The mysql dialect's rules are used throughout, as the dialect that has them.
Every case was checked against the mysql 8.4 and 9.7 and mariadb 11.8 clients.
"""

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.parser import PyLexer
from sqlfluff.core.parser.client_commands import (
    ClientCommand,
    ClientCommandRules,
    CommandEffect,
    EmittedToken,
)

RULES = ClientCommandRules(
    commands=(
        ClientCommand(CommandEffect.SET_DELIMITER, name="delimiter", shorthand="\\d"),
        ClientCommand(CommandEffect.END_STATEMENT, shorthand="\\g"),
    ),
    opaque_token_names=frozenset(),
    command_after_block_comment=True,
    dash_dash_comment_at_statement_start=False,
)


def test_client_commands_long_forms_match_in_any_case():
    """Long forms are found in any case, short forms only in their own."""
    assert RULES.command_named("DeLiMiTeR") is RULES.commands[0]
    assert RULES.command_named("source") is None
    assert RULES.command_starting("\\g;") is RULES.commands[1]
    assert RULES.command_starting("\\G;") is None


def test_client_commands_emitted_tokens_never_match():
    """An emitted token kind isn't a matcher."""
    with pytest.raises(NotImplementedError):
        EmittedToken("delimiter_argument").match("anything")


def _tokens(raw: str, dialect: str = "mysql") -> list[tuple[str, str]]:
    """The (type, raw) of each token the Python lexer makes, but whitespace."""
    lexer = PyLexer(config=FluffConfig(overrides={"dialect": dialect}))
    segments, errors = lexer.lex(raw)
    assert not errors
    return [
        (segment.get_type(), segment.raw)
        for segment in segments
        if segment.get_type() not in ("whitespace", "newline", "end_of_file")
    ]


@pytest.mark.parametrize(
    "raw, expected",
    [
        # The delimiter is found inside words and needs no space before it.
        (
            "DELIMITER go\nSELECT good go\n",
            [
                ("word", "DELIMITER"),
                ("delimiter_argument", "go"),
                ("word", "SELECT"),
                ("client_delimiter", "go"),
                ("word", "od"),
                ("client_delimiter", "go"),
            ],
        ),
        # A backslash escapes the next character in an unquoted argument.
        (
            "DELIMITER a\\ b\nSELECT 1 a b\n",
            [
                ("word", "DELIMITER"),
                ("delimiter_argument", "a\\ b"),
                ("word", "SELECT"),
                ("numeric_literal", "1"),
                ("client_delimiter", "a b"),
            ],
        ),
        # A delimiter over 15 bytes is cut, here before a two-byte character.
        (
            "DELIMITER ééééééééx\nSELECT 1 ééééééé\n",
            [
                ("word", "DELIMITER"),
                ("delimiter_argument", "ééééééééx"),
                ("word", "SELECT"),
                ("numeric_literal", "1"),
                ("client_delimiter", "ééééééé"),
            ],
        ),
        # After `\d` the client goes on from the first copy of the new
        # delimiter, which here is the argument itself.
        (
            "\\d $$ SELECT 1 $$\n",
            [
                ("client_command_shorthand", "\\d"),
                ("delimiter_argument", "$$"),
                ("word", "SELECT"),
                ("numeric_literal", "1"),
                ("client_delimiter", "$$"),
            ],
        ),
        # `--` right before the end of a statement is a comment.
        (
            "SELECT 1 --\\g\n",
            [
                ("word", "SELECT"),
                ("numeric_literal", "1"),
                ("inline_comment", "--"),
                ("client_command_shorthand", "\\g"),
            ],
        ),
        # A token is lexed from the text the server gets, which ends at the
        # delimiter: `1.` and `.5` are numbers.
        (
            "DELIMITER go\nSELECT 1.go\nSELECT .5go\n",
            [
                ("word", "DELIMITER"),
                ("delimiter_argument", "go"),
                ("word", "SELECT"),
                ("numeric_literal", "1."),
                ("client_delimiter", "go"),
                ("word", "SELECT"),
                ("numeric_literal", ".5"),
                ("client_delimiter", "go"),
            ],
        ),
        # After a delimiter on the same line, SOURCE runs to the next one.
        (
            "SELECT 1; SOURCE b.sql;\n",
            [
                ("word", "SELECT"),
                ("numeric_literal", "1"),
                ("semicolon", ";"),
                ("word", "SOURCE"),
                ("source_file_name", "b.sql"),
                ("semicolon", ";"),
            ],
        ),
        # With `\g` on its line, SOURCE is collected as a statement, so the
        # client doesn't read this file name.
        (
            "SOURCE a.sql \\g\n",
            [("word", "SOURCE"), ("client_command_misread", "a.sql \\g")],
        ),
    ],
)
def test_client_commands_lexing(raw: str, expected: list[tuple[str, str]]):
    """Test the tokens the client command scanner makes."""
    assert _tokens(raw) == expected


def test_client_commands_dash_dash_at_mariadb_statement_start():
    """The mariadb client takes `--` at the start of a statement as a comment."""
    raw = "SELECT 1; --x\n"
    assert _tokens(raw, "mariadb")[-1] == ("inline_comment", "--x")
    assert _tokens(raw, "mysql")[-3:] == [
        ("minus", "-"),
        ("minus", "-"),
        ("word", "x"),
    ]


def test_client_commands_delimiter_inside_a_dollar_quote():
    """The mysql client doesn't find the delimiter in a dollar-quoted string.

    MariaDB has no dollar-quoted strings, so its client does.
    """
    raw = "DELIMITER ;;\nSELECT $js$ a ;; b $js$;;\n"
    assert _tokens(raw)[2:] == [
        ("word", "SELECT"),
        ("dollar_quote", "$js$ a ;; b $js$"),
        ("client_delimiter", ";;"),
    ]
    assert _tokens(raw, "mariadb")[2:6] == [
        ("word", "SELECT"),
        ("word", "$js$"),
        ("word", "a"),
        ("client_delimiter", ";;"),
    ]
