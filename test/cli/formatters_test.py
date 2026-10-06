"""The Test file for CLI Formatters."""

import pathlib
import re
import textwrap

import pytest

from sqlfluff.cli.commands import fix
from sqlfluff.cli.formatters import OutputStreamFormatter
from sqlfluff.cli.outputstream import FileOutput, OutputKind, OutputPolicy
from sqlfluff.core import FluffConfig
from sqlfluff.core.errors import SQLLintError
from sqlfluff.core.parser import RawSegment
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.rules import RuleGhost
from sqlfluff.core.templaters.base import TemplatedFile
from sqlfluff.core.types import Color


@pytest.mark.parametrize(
    ("policy", "kind", "minimum_verbosity", "expected"),
    [
        (OutputPolicy(), OutputKind.STATUS, 0, True),
        (OutputPolicy(quiet=True), OutputKind.PAYLOAD, 0, True),
        (OutputPolicy(quiet=True), OutputKind.DIAGNOSTIC, 0, True),
        (OutputPolicy(quiet=True), OutputKind.ACTION, 0, True),
        (OutputPolicy(quiet=True), OutputKind.STATUS, 0, False),
        (OutputPolicy(quiet=True), OutputKind.PROGRESS, 0, False),
        (OutputPolicy(), OutputKind.VERBOSE, 1, False),
        (OutputPolicy(verbosity=1), OutputKind.VERBOSE, 1, True),
        (OutputPolicy(verbosity=1), OutputKind.VERBOSE, 2, False),
        (OutputPolicy(verbosity=2), OutputKind.VERBOSE, 2, True),
        (OutputPolicy(verbosity=2, quiet=True), OutputKind.VERBOSE, 1, False),
        (OutputPolicy(machine_output=True), OutputKind.PAYLOAD, 0, True),
        (OutputPolicy(machine_output=True), OutputKind.DIAGNOSTIC, 0, False),
    ],
)
def test__cli__output_policy(policy, kind, minimum_verbosity, expected):
    """Output policy should filter semantic categories independently."""
    assert policy.allows(kind, minimum_verbosity=minimum_verbosity) is expected


def escape_ansi(line):
    """Remove ANSI color codes for testing."""
    ansi_escape = re.compile("\u001b\\[[0-9]+(;[0-9]+)?m")
    return ansi_escape.sub("", line)


def test__cli__formatters__filename_nocol(tmpdir):
    """Test formatting filenames."""
    formatter = OutputStreamFormatter(
        FileOutput(FluffConfig(require_dialect=False), str(tmpdir / "out.txt")),
        False,
        OutputPolicy(),
    )
    res = formatter.format_filename("blahblah", success=True)
    assert escape_ansi(res) == "== [blahblah] PASS"


def test__cli__formatters__violation(tmpdir):
    """Test formatting violations.

    NB Position is 1 + start_pos.
    """
    s = RawSegment(
        "foobarbar",
        PositionMarker(
            slice(10, 19),
            slice(10, 19),
            TemplatedFile.from_string("      \n\n  foobarbar"),
        ),
    )
    r = RuleGhost("A", "some-name", "DESC")
    v = SQLLintError(description=r.description, segment=s, rule=r)
    formatter = OutputStreamFormatter(
        FileOutput(FluffConfig(require_dialect=False), str(tmpdir / "out.txt")),
        False,
        OutputPolicy(),
    )
    f = formatter.format_violation(v)
    # Position is 3, 3 because foobarbar is on the third
    # line (i.e. it has two newlines preceding it) and
    # it's at the third position in that line (i.e. there
    # are two characters between it and the preceding
    # newline).
    assert escape_ansi(f) == "L:   3 | P:   3 |    A | DESC [some-name]"


def test__cli__helpers__colorize(tmpdir):
    """Test ANSI colouring."""
    formatter = OutputStreamFormatter(
        FileOutput(FluffConfig(require_dialect=False), str(tmpdir / "out.txt")),
        False,
        OutputPolicy(),
    )
    # Force color output for this test.
    formatter.plain_output = False
    assert formatter.colorize("foo", Color.red) == "\u001b[31mfoo\u001b[0m"


@pytest.mark.parametrize(
    "nocolor,isatty,no_color_env,expected_plain_output",
    [
        (None, True, None, False),
        (None, False, None, True),
        (True, True, None, True),
        (False, False, None, False),
        (False, False, "1", False),
        (None, True, "1", True),
    ],
)
def test__cli__helpers__plain_output_color_decision(
    monkeypatch, nocolor, isatty, no_color_env, expected_plain_output
):
    """Test when output should be plain rather than colored."""
    monkeypatch.setattr("sys.stdout.isatty", lambda: isatty)
    if no_color_env is None:
        monkeypatch.delenv("NO_COLOR", raising=False)
    else:
        monkeypatch.setenv("NO_COLOR", no_color_env)

    assert (
        OutputStreamFormatter.should_produce_plain_output(nocolor)
        is expected_plain_output
    )


def test__cli__helpers__cli_table(tmpdir):
    """Test making tables."""
    vals = [("a", 3), ("b", "c"), ("d", 4.7654), ("e", 9)]
    formatter = OutputStreamFormatter(
        FileOutput(FluffConfig(require_dialect=False), str(tmpdir / "out.txt")),
        False,
        OutputPolicy(),
    )
    txt = formatter.cli_table(vals, col_width=7, divider_char="|", label_color=None)
    # NB: No trailing newline
    assert txt == "a:    3|b:    c\nd: 4.77|e:    9"


@pytest.mark.parametrize(
    "sql,fix_args,expected",
    [
        (
            (
                "CREATE TABLE IF NOT EXISTS vuln.software_name_dictionary("
                "id SERIAL PRIMARY KEY"
                "rule VARCHAR(30)"
                ");"
            ),
            ["--force", "--dialect", "postgres", "--disable-progress-bar", "--nocolor"],
            (
                "CREATE TABLE IF NOT EXISTS vuln.software_name_dictionary("
                "id SERIAL PRIMARY KEY"
                "rule VARCHAR(30)"
                ");"
            ),
        )
    ],
)
def test__cli__fix_no_corrupt_file_contents(sql, fix_args, expected, tmpdir):
    """Test how the fix cli command creates files.

    Ensure there is no incorrect output from stderr
    that makes it to the file.
    """
    tmp_path = pathlib.Path(str(tmpdir))
    filepath = tmp_path / "testing.sql"
    filepath.write_text(textwrap.dedent(sql))

    with tmpdir.as_cwd():
        with pytest.raises(SystemExit):
            fix(fix_args)
    with open(tmp_path / "testing.sql", "r") as fin:
        actual = fin.read()

    # Ensure no corruption in formatted file
    assert actual.strip() == expected.strip()
