"""Tests for lexing scripts run through a command-line client.

The mysql dialect's rules are used throughout, as the dialect that has them.
Every case was checked against the mysql 8.4 and 9.7 and mariadb 11.8 clients.
"""

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.parser import ClientTextSegment, PyLexer
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
    line_command_after_block_comment=True,
    dash_dash_comment_at_statement_start=False,
    collected_line_marker="\\g",
)


def test_client_commands_no_long_form_ends_a_statement():
    """A long form that ends a statement would do nothing, so the rules refuse it."""
    with pytest.raises(ValueError, match="'go' can't end a statement"):
        ClientCommandRules(
            commands=(ClientCommand(CommandEffect.END_STATEMENT, name="go"),),
            opaque_token_names=frozenset(),
            line_command_after_block_comment=True,
            dash_dash_comment_at_statement_start=False,
            collected_line_marker="\\g",
        )


def test_client_commands_long_forms_match_in_any_case():
    """Long forms are found in any case, short forms only in their own."""
    assert RULES.command_named("DeLiMiTeR") is RULES.commands[0]
    assert RULES.command_named("source") is None
    assert RULES.command_starting("\\g;") is RULES.commands[1]
    assert RULES.command_starting("\\G;") is None


def test_client_commands_emitted_tokens_never_match():
    """An emitted token kind isn't a matcher."""
    token = EmittedToken("delimiter_argument", ClientTextSegment)
    with pytest.raises(NotImplementedError):
        token.match("anything")
    with pytest.raises(NotImplementedError):
        token.search("anything")


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
        # A short command adds nothing to the statement, so a command can
        # follow it.
        (
            "\\d $$\nDELIMITER ;\n",
            [
                ("client_command_shorthand", "\\d"),
                ("delimiter_argument", "$$"),
                ("word", "DELIMITER"),
                ("delimiter_argument", ";"),
            ],
        ),
        # `\d` with no argument is refused, and the delimiter kept.
        (
            "\\d\nSELECT 1;\n",
            [
                ("client_command_shorthand", "\\d"),
                ("word", "SELECT"),
                ("numeric_literal", "1"),
                ("semicolon", ";"),
            ],
        ),
        # A quoted argument with no closing quote runs to the end of the line.
        (
            "DELIMITER 'ab\nSELECT 1 ab\n",
            [
                ("word", "DELIMITER"),
                ("delimiter_argument", "'ab"),
                ("word", "SELECT"),
                ("numeric_literal", "1"),
                ("client_delimiter", "ab"),
            ],
        ),
        # A line that holds `\g` is collected as a statement, even DELIMITER's:
        # this one is SQL, not a command. `\G` doesn't count, so SOURCE takes
        # its line and the file name ends in `\G`.
        (
            "DELIMITER // \\g\nSOURCE a.sql \\G\n",
            [
                ("word", "DELIMITER"),
                ("divide", "/"),
                ("divide", "/"),
                ("client_command_shorthand", "\\g"),
                ("word", "SOURCE"),
                ("source_file_name", "a.sql \\G"),
            ],
        ),
        # `\g` right after SOURCE sends `SOURCE` alone to the server.
        (
            "SOURCE \\g\n",
            [("word", "SOURCE"), ("client_command_shorthand", "\\g")],
        ),
        # Trailing whitespace isn't part of a file name.
        (
            "SOURCE a.sql \t \n",
            [("word", "SOURCE"), ("source_file_name", "a.sql")],
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
        # client doesn't read this file name. The `\g` sends `SOURCE a.sql`
        # to the server and ends the statement, so the next line can be a
        # command.
        (
            "SOURCE a.sql \\g\nDELIMITER $$\nSELECT 1 $$\n",
            [
                ("word", "SOURCE"),
                ("client_command_misread", "a.sql"),
                ("client_command_shorthand", "\\g"),
                ("word", "DELIMITER"),
                ("delimiter_argument", "$$"),
                ("word", "SELECT"),
                ("numeric_literal", "1"),
                ("client_delimiter", "$$"),
            ],
        ),
    ],
)
def test_client_commands_lexing(raw: str, expected: list[tuple[str, str]]):
    """Test the tokens the client script lexer makes."""
    assert _tokens(raw) == expected


def test_client_commands_mariadb_collected_command_after_a_comment():
    """A comment can come before a command the client collects as a statement.

    The mariadb client doesn't take a command after a comment on its line,
    but it does check a collected statement for one.
    """
    assert _tokens("/* c */ SOURCE a.sql;\n", "mariadb") == [
        ("block_comment", "/* c */"),
        ("word", "SOURCE"),
        ("source_file_name", "a.sql"),
        ("semicolon", ";"),
    ]


def test_client_commands_unlexable_text():
    """Text that no matcher takes is unlexable, as in any other dialect."""
    lexer = PyLexer(config=FluffConfig(overrides={"dialect": "mysql"}))
    segments, errors = lexer.lex("SELECT 1 \x01;\n")
    assert [segment.raw for segment in segments if segment.is_type("unlexable")] == [
        "\x01"
    ]
    assert errors


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
