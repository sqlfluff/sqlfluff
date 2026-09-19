"""Validate SQL against a real database engine.

sqlfluff's dialect fixtures are mostly provided through contributions.
Often, maintainers don't have access to all database engine's and can't
validate the correctness themselves. A fixture can end up asserting
that sqlfluff parses some SQL as valid when the real engine would not.
This script allows checking SQL against the real engines with minimal
configuration for syntactical correctness.

Run it with `uv run --group fixture-validation`, naming the dialects to
check, e.g.:

    uv run --group fixture-validation python utils/validate_fixtures.py --dialects duckdb postgres sqlite

It prints a Markdown report of any statement a real engine's own parser
rejects, even though sqlfluff's grammar accepts it.

By default it scans every fixture file for the named dialects. Use
`--changed-files PATH` (or `-` for stdin) to narrow that down to only
fixtures that changed, e.g. piping in `git diff --name-only`:

    git diff --name-only main... | uv run --group fixture-validation python utils/validate_fixtures.py --changed-files -

Or use `--sql PATH` (or `-` for stdin) to check raw SQL directly instead of
scanning fixtures at all, e.g.:

    echo "SELECT 1;" | uv run --group fixture-validation python utils/validate_fixtures.py --dialects postgres --sql -

Limitations: currently only duckdb, postgres, and sqlite are supported,
this approach only catches syntax errors and not semantic ones (missing
tables/columns, etc.).
"""

import argparse
import os
import re
import sqlite3
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator, Optional

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.linter import RenderedFile
from sqlfluff.core.templaters import TemplatedFile

try:
    import duckdb
except ImportError:
    duckdb = None

try:
    import pglast
except ImportError:
    pglast = None

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "test" / "fixtures" / "dialects"
FIXTURE_FILE_RE = re.compile(r"test/fixtures/dialects/(?P<name>[^/]+)/[^/]+\.sql$")


def _require(module, package: str, *, note: str = "") -> None:
    """Raise RuntimeError with a standard install hint if `module` is None."""
    if module is not None:
        return
    raise RuntimeError(
        f"{package} is not installed{note}. Run this script with "
        f"`uv run --group fixture-validation "
        f"python utils/validate_fixtures.py ...`."
    )


@contextmanager
def _scratch_cwd() -> Iterator[None]:
    """Temporarily chdir into a fresh scratch directory, then restore cwd.

    Some fixture statements have real filesystem side effects when executed,
    so a checker that executes SQL runs from a throwaway temp directory
    rather than the caller's working directory.
    """
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as scratch_dir:
        os.chdir(scratch_dir)
        try:
            yield
        finally:
            os.chdir(cwd)


def check_duckdb(sql: str) -> Optional[str]:
    """Return an error message if DuckDB's real parser rejects `sql`.

    Returns None if it accepts it (including if it fails for a non-syntax
    reason - DuckDB has no pure-parse API for non-SELECT statements, so this
    executes against a scratch in-memory database and only treats a
    ParserException as a divergence).
    """
    _require(duckdb, "duckdb")
    result: Optional[str] = None
    with _scratch_cwd():
        con = duckdb.connect(":memory:")
        try:
            con.execute(sql)
        except duckdb.ParserException as err:
            result = str(err)
        except duckdb.Error:
            pass  # Non-syntax error - not this tool's concern.
        finally:
            # Close the connection before the temp dir goes out of scope,
            # otherwise Windows refuses to remove a directory that still
            # has open file handles in it.
            con.close()
    return result


def check_postgres(sql: str) -> Optional[str]:
    """Return an error message if Postgres's real parser rejects `sql`.

    Returns None if it accepts it. Unlike DuckDB, `pglast` (which bundles
    `libpg_query`) is a pure parser with no execution involved, so there's
    no schema/semantic ambiguity and no filesystem side effects to guard
    against - any rejection is a genuine syntax divergence.
    """
    _require(pglast, "pglast")
    try:
        pglast.parse_sql(sql)
    except pglast.Error as err:
        return str(err)
    return None


def check_sqlite(sql: str) -> Optional[str]:
    """Return an error message if SQLite's real parser rejects `sql`.

    Returns None if it accepts it (including if it fails for a non-syntax
    reason). Unlike DuckDB, sqlite3 doesn't distinguish a syntax error from
    other operational errors (e.g. a missing table) by exception type - both
    raise `sqlite3.OperationalError` - so this filters by message content
    instead: only a message containing "syntax error" counts as a
    divergence.
    """
    result: Optional[str] = None
    with _scratch_cwd():
        con = sqlite3.connect(":memory:")
        try:
            con.execute(sql)
        except sqlite3.Error as err:
            message = str(err)
            if "syntax error" in message:
                result = message
        finally:
            # Close before the temp dir is removed - see check_duckdb.
            con.close()
    return result


CHECKERS: dict[str, Callable[[str], Optional[str]]] = {
    "duckdb": check_duckdb,
    "postgres": check_postgres,
    "sqlite": check_sqlite,
}


def fixture_paths_from_changed_files(paths: list[str]) -> dict[str, list[Path]]:
    """Group changed fixture file paths by dialect.

    Only paths matching `test/fixtures/dialects/<dialect>/*.sql` count;
    anything else (e.g. an unrelated file swept up by a broader `git diff`)
    is ignored. Returned paths are resolved relative to the repo root so
    they work regardless of the caller's own working directory.
    """
    repo_root = FIXTURES_DIR.parents[2]
    by_dialect: dict[str, list[Path]] = {}
    for path in paths:
        match = FIXTURE_FILE_RE.search(path)
        if match:
            by_dialect.setdefault(match.group("name"), []).append(repo_root / path)
    return by_dialect


def iter_statements_from_sql(dialect: str, raw: str) -> Iterator[tuple[int, str]]:
    """Yield (line_no, raw_sql) for each statement in `raw`.

    `raw` is treated as plain SQL, not a Jinja template, even though
    sqlfluff's default templater is Jinja - some legitimate SQL (e.g. nested
    array literals) can confuse it. So this bypasses templating entirely, the
    same way existing dialect fixture tests do
    (test/dialects/dialects_test.py's `lex_and_parse`), by handing the
    parser an already-rendered file.
    """
    config = FluffConfig(overrides={"dialect": dialect})
    templated_file = TemplatedFile.from_string(raw)
    rendered_file = RenderedFile(
        [templated_file], [], config, {}, templated_file.fname, "utf8", raw
    )
    parsed = Linter(config=config).parse_rendered(rendered_file)
    for statement in parsed.tree.recursive_crawl("statement", recurse_into=False):
        yield statement.pos_marker.working_line_no, statement.raw


def iter_statements(dialect: str, sql_path: Path) -> Iterator[tuple[int, str]]:
    """Yield (line_no, raw_sql) for each statement in `sql_path`."""
    raw = sql_path.read_text(encoding="utf-8")
    yield from iter_statements_from_sql(dialect, raw)


def run(
    dialects: set[str],
    *,
    fixture_paths: Optional[dict[str, list[Path]]] = None,
) -> tuple[list[str], list[str], list[tuple[str, str, int, str, str]]]:
    """Check fixture examples for `dialects`.

    By default, `fixture_paths=None` checks every `*.sql` fixture under
    each dialect's fixture directory. Pass `fixture_paths` (as returned by
    `fixture_paths_from_changed_files`) to instead check only those specific
    files per dialect - e.g. to scope a PR's validation run to just the
    fixture files it actually touched, rather than that dialect's whole
    fixture set.

    Returns (checked_dialects, skipped_dialects, findings), where each
    finding is (dialect, file, line, sql, error).
    """
    checked = []
    skipped = []
    findings = []
    for dialect in sorted(dialects):
        checker = CHECKERS.get(dialect)
        if checker is None:
            skipped.append(dialect)
            continue
        checked.append(dialect)
        if fixture_paths is not None:
            sql_paths = sorted(fixture_paths.get(dialect, []))
        else:
            sql_paths = sorted((FIXTURES_DIR / dialect).glob("*.sql"))
        for sql_path in sql_paths:
            if not sql_path.is_file():
                continue
            for line_no, sql in iter_statements(dialect, sql_path):
                error = checker(sql)
                if error is not None:
                    rel_path = sql_path.relative_to(FIXTURES_DIR.parents[1])
                    findings.append((dialect, rel_path.as_posix(), line_no, sql, error))
    return checked, skipped, findings


def run_sql(
    dialects: set[str], raw: str
) -> tuple[list[str], list[str], list[tuple[str, str, int, str, str]]]:
    """Check ad-hoc SQL text `raw` against each of `dialects`.

    Same return shape as `run`, but checks the statements parsed from `raw`
    directly instead of globbing fixture files - findings use the label
    "<ad-hoc input>" in place of a fixture file path.
    """
    checked = []
    skipped = []
    findings = []
    for dialect in sorted(dialects):
        checker = CHECKERS.get(dialect)
        if checker is None:
            skipped.append(dialect)
            continue
        checked.append(dialect)
        for line_no, sql in iter_statements_from_sql(dialect, raw):
            error = checker(sql)
            if error is not None:
                findings.append((dialect, "<ad-hoc input>", line_no, sql, error))
    return checked, skipped, findings


def format_report(
    checked: list[str],
    skipped: list[str],
    findings: list[tuple[str, str, int, str, str]],
) -> str:
    """Format the results of `run` as a Markdown report."""
    lines = ["# Dialect SQL Example Validation"]
    if checked:
        lines.append(f"Checked against a real engine: {', '.join(checked)}")
    if skipped:
        lines.append(f"No real-engine validator available yet: {', '.join(skipped)}")
    if not checked and not skipped:
        lines.append("No dialect fixtures needed checking.")
    if findings:
        lines.append("")
        lines.append("| Dialect | File | SQL | Error |")
        lines.append("|---|---|---|---|")
        for dialect, file, line_no, sql, error in findings:
            sql_cell = sql.replace("|", "\\|").replace("\n", " ")
            error_cell = error.replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {dialect} | {file}:{line_no} | `{sql_cell}` | {error_cell} |"
            )
    elif checked:
        lines.append("")
        lines.append("No divergences found.")
    return "\n".join(lines) + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--dialects",
        nargs="+",
        help="Dialect names to check (e.g. duckdb postgres sqlite).",
    )
    group.add_argument(
        "--changed-files",
        metavar="PATH",
        help=(
            "File of changed paths (one per line), or '-' for stdin, e.g. "
            "the output of `git diff --name-only`. Only the "
            "test/fixtures/dialects/<dialect>/*.sql paths in it are "
            "checked - not every fixture for a dialect any of them belong "
            "to."
        ),
    )
    parser.add_argument(
        "--exclude-dialects",
        nargs="+",
        default=[],
        help="Dialect names to never check here even if named/derived above.",
    )
    parser.add_argument(
        "--sql",
        metavar="PATH",
        help=(
            "File of raw SQL to check (or '-' for stdin), instead of "
            "scanning fixture files. Use together with --dialects."
        ),
    )
    args = parser.parse_args(argv)

    if args.changed_files == "-" and args.sql == "-":
        parser.error("--changed-files - and --sql - cannot both read from stdin.")

    fixture_paths = None
    if args.changed_files:
        text = (
            sys.stdin.read()
            if args.changed_files == "-"
            else Path(args.changed_files).read_text(encoding="utf-8")
        )
        fixture_paths = fixture_paths_from_changed_files(text.splitlines())
        dialects = set(fixture_paths)
    else:
        dialects = set(args.dialects)
    dialects -= set(args.exclude_dialects)
    if fixture_paths is not None:
        fixture_paths = {d: p for d, p in fixture_paths.items() if d in dialects}

    if args.sql:
        raw = (
            sys.stdin.read()
            if args.sql == "-"
            else Path(args.sql).read_text(encoding="utf-8")
        )
        checked, skipped, findings = run_sql(dialects, raw)
    else:
        checked, skipped, findings = run(dialects, fixture_paths=fixture_paths)
    print(format_report(checked, skipped, findings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
