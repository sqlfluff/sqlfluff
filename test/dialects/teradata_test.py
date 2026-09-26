"""Tests specific to the Teradata dialect."""

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.fixture(scope="module")
def teradata_linter() -> Linter:
    """A Linter configured for the Teradata dialect."""
    return Linter(config=FluffConfig(overrides={"dialect": "teradata"}))


@pytest.mark.parametrize(
    "raw,command",
    [
        # A dot-command terminated only by the end of its line (no semicolon)
        # followed by a semicolon-terminated SQL statement.
        (
            ".LOGON tdpid/username,password\nSELECT 1;\n",
            ".LOGON tdpid/username,password",
        ),
        # A no-argument dot-command followed by SQL.
        (".LOGOFF\nSELECT 1;\n", ".LOGOFF"),
        # A dot-command directly followed by another dot-command, both
        # newline-terminated.
        (".SET WIDTH 254\n.LOGOFF\nSELECT 1;\n", ".SET WIDTH 254"),
    ],
)
def test_bteq_command_is_newline_separated(
    teradata_linter: Linter, raw: str, command: str
) -> None:
    """BTEQ dot-commands are terminated by the end of their line.

    A dot-command needs no semicolon; the following statement parses
    independently rather than being absorbed or reported as unparsable
    (see #1673).
    """
    parsed = teradata_linter.parse_string(raw)

    # The whole script parses cleanly.
    assert not parsed.violations

    bteq_statements = list(parsed.tree.recursive_crawl("bteq_statement"))
    select_statements = list(parsed.tree.recursive_crawl("select_statement"))
    # The dot-command is bounded to its own line and the SELECT is a separate
    # statement (not swallowed by the command).
    assert bteq_statements[0].raw == command
    assert "SELECT" not in bteq_statements[0].raw
    assert len(select_statements) == 1


@pytest.mark.parametrize(
    "raw,first_command",
    [
        # A command with structured arguments, followed by a command the
        # argument grammar would happily keep matching if it were allowed to
        # run past the end of the line.
        (
            ".IF ERRORCODE <> 0 THEN .QUIT 1\n.LABEL LOADSTEP\n",
            ".IF ERRORCODE <> 0 THEN .QUIT 1",
        ),
        (
            ".IF ACTIVITYCOUNT = 0 THEN .QUIT 2\n.EXPORT DATA FILE=out.dat\n",
            ".IF ACTIVITYCOUNT = 0 THEN .QUIT 2",
        ),
        # A bare keyword command followed by a literal on the next line.
        (".QUIT\n.RUN FILE=POSTING\n", ".QUIT"),
    ],
)
def test_bteq_arguments_stop_at_the_end_of_the_line(
    teradata_linter: Linter, raw: str, first_command: str
) -> None:
    """A dot-command's arguments never reach onto the following line.

    The argument grammar skips whitespace, and a newline is just whitespace,
    so without a line boundary a command would carry on matching keywords into
    the command below it.
    """
    parsed = teradata_linter.parse_string(raw)

    assert not parsed.violations

    bteq_statements = list(parsed.tree.recursive_crawl("bteq_statement"))
    assert len(bteq_statements) == 2
    assert bteq_statements[0].raw == first_command


def test_modelled_and_generic_command_words_have_distinct_types(
    teradata_linter: Linter,
) -> None:
    """A modelled keyword is distinguishable from an arbitrary command word.

    `.LOGON` is one of the control-flow commands the grammar models, while
    `.SET` and anything misspelled is matched by the generic catch-all. The
    two must not share a segment type, or anything keyed on the modelled
    keywords silently applies to opaque words as well.
    """
    parsed = teradata_linter.parse_string(
        ".LOGON tdpid\n.SET WIDTH 254\n.NOSUCHCMD x\n"
    )

    assert not parsed.violations

    keywords = [s.raw for s in parsed.tree.recursive_crawl("bteq_key_word_segment")]
    command_names = [s.raw for s in parsed.tree.recursive_crawl("bteq_command_name")]
    assert keywords == ["LOGON"]
    assert command_names == ["SET", "NOSUCHCMD"]


def test_bteq_keyword_does_not_take_a_literal_from_the_next_line(
    teradata_linter: Linter,
) -> None:
    """A keyword command takes its literal argument from its own line only.

    `.QUIT 1` is one command, but `.QUIT` on its own line must not reach down
    and use a number from the line below as its argument.
    """
    parsed = teradata_linter.parse_string(".QUIT\n100\n")

    bteq_statements = list(parsed.tree.recursive_crawl("bteq_statement"))
    assert [s.raw for s in bteq_statements] == [".QUIT"]
    # The stray number is left over, and reported rather than absorbed.
    assert list(parsed.tree.recursive_crawl("unparsable"))


@pytest.mark.parametrize(
    "raw",
    [
        # Two SELECTs. The first matches greedily across the newline, so this
        # would fail even without an explicit terminator requirement.
        "SELECT 1 FROM t\nSELECT 2 FROM t\n",
        # Statements which cannot absorb the following line, so they only fail
        # if the terminator is genuinely required rather than incidentally
        # enforced by greedy matching.
        "DATABASE mydb\nSELECT 1;\n",
        "DATABASE a\nDATABASE b;\n",
        "DELETE FROM t ALL\nSELECT 1;\n",
        "SET SESSION DATABASE mydb\nSELECT 1;\n",
    ],
)
def test_sql_statements_still_require_a_semicolon(
    teradata_linter: Linter, raw: str
) -> None:
    """Newline separation does not relax semicolon termination for SQL.

    Only BTEQ dot-commands are newline-terminated. Two SQL statements with no
    semicolon between them are still reported as unparsable, including the
    cases where the first statement cannot swallow the second one on its own.
    """
    parsed = teradata_linter.parse_string(raw)

    assert any(v.rule_code() == "PRS" for v in parsed.violations)


@pytest.mark.parametrize(
    "raw,statements",
    [
        # A file's last statement may leave off its semicolon, as in ansi.
        ("SELECT 1 FROM t\n", 1),
        ("SELECT 1 FROM t;\nSELECT 2 FROM t\n", 2),
        # A dot-command needs no semicolon wherever it appears.
        (".LOGOFF\nDATABASE mydb;\n", 2),
        ("SELECT 1 FROM t;\n.LOGOFF\n", 2),
    ],
)
def test_optional_terminators_still_parse(
    teradata_linter: Linter, raw: str, statements: int
) -> None:
    """Requiring a terminator for SQL does not over-tighten the grammar.

    A trailing statement at the end of the file may still omit its semicolon,
    and dot-commands never need one.
    """
    parsed = teradata_linter.parse_string(raw)

    assert not parsed.violations
    assert len(list(parsed.tree.recursive_crawl("statement"))) == statements
