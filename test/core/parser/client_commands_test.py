"""Tests for lexing scripts run through a command-line client."""

import pytest

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
