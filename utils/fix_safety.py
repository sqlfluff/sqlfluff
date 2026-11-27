#!/usr/bin/env python3
"""Flag fixes that may change what a query means, for review.

For each statement in a dialect's parse fixtures, this runs ``sqlfluff fix``
with every rule except those in ``EXCLUDED_RULES``, whose fixes change the tree
on purpose. It then asks the real database's own parser, an *oracle*, for the
syntax tree of the statement before and after the fix. If the trees differ, or
the database can't parse the fixed statement, the fix is flagged as a possible
unsafe change, and it's run again with one rule at a time to name the rules.

A flagged fix needs a person to look at it: two different trees can still mean
the same thing. And a fix that isn't flagged isn't proven safe: the check only
sees the statements in the fixtures, with the default rule settings, without
templating, and can't judge the excluded rules or what a dialect does beyond
what its parser shows (DuckDB's ``json_serialize_sql`` only handles SELECTs).

Failures listed in ``utils/fix_safety_known_failures.yml`` are reported but
don't fail the run. Entries that no longer fail are reported too, so the list
can be kept up to date.

Exit codes: 1 when there are new failures, or listed ones that pass; otherwise
3 when the run is incomplete, because fixing a statement timed out or raised,
and 0 when it isn't. 2 when a dialect has no oracle, the oracle is missing, or
no fixture file matches.

Usage:
    python utils/fix_safety.py --dialect duckdb --dialect postgres
    python utils/fix_safety.py --dialect duckdb --rules LT01,CV11
    python utils/fix_safety.py --dialect duckdb --filter "select*" --report out.md

Oracles need their database parser installed (``pip install duckdb``); the
``fix-safety`` tox environment installs them.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import signal
import sys
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import yaml

from sqlfluff.core import FluffConfig, Linter

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "test" / "fixtures" / "dialects"
KNOWN_FAILURES = Path(__file__).resolve().parent / "fix_safety_known_failures.yml"

# Rules whose fix is meant to change the syntax tree while keeping the result,
# so comparing trees can't judge them. Each needs a reason.
EXCLUDED_RULES: dict[str, str] = {
    "AL05": "removes an unused table alias",
    "AL07": "replaces table aliases with table names",
    "AL09": "removes a column alias that's the same as the column",
    "AM03": "writes the default sort order (ASC) explicitly",
    "CV02": "replaces IFNULL and NVL with COALESCE",
    "CV04": "replaces COUNT(1) with COUNT(*)",
    "CV05": "replaces `= NULL` with `IS NULL`, which changes the result on purpose",
    "RF03": "qualifies or unqualifies column references",
    "ST01": "removes a redundant `ELSE NULL`",
    "ST02": "rewrites a CASE as COALESCE or a condition",
    "ST04": "flattens nested CASE expressions",
    "ST05": "moves subqueries into CTEs",
    "ST06": "reorders the columns of a SELECT",
    "ST07": "replaces USING with ON",
    "ST09": "swaps the sides of a join condition",
}

# Seconds allowed for linting and fixing one statement.
STATEMENT_TIMEOUT = 30


class Oracle:
    """A database's own parser, used to judge whether two statements match."""

    name: str = ""
    dialects: tuple[str, ...] = ()

    @classmethod
    def available(cls) -> bool:
        """Whether the database's parser is installed."""
        raise NotImplementedError  # pragma: no cover

    def tree(self, sql: str) -> Optional[str]:
        """Return a canonical syntax tree for one statement.

        Returns None when the oracle can't parse the statement, or can't judge
        it (for example a statement kind it doesn't serialise).
        """
        raise NotImplementedError  # pragma: no cover


def _drop_keys(obj: Any, is_position: Callable[[str, Any], bool]) -> Any:
    """Recursively drop the dict entries that `is_position` says are positions."""
    if isinstance(obj, dict):
        return {
            k: _drop_keys(v, is_position)
            for k, v in obj.items()
            if not is_position(k, v)
        }
    if isinstance(obj, list):
        return [_drop_keys(v, is_position) for v in obj]
    return obj


_ASCII_LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")


def _fold_identifiers(obj: Any) -> Any:
    """Lower-case the ASCII letters of every string in a DuckDB tree.

    DuckDB resolves identifiers without regard to the case of ASCII letters,
    quoted or not, but its serialised tree keeps the case they were written in.
    Other letters keep their case, because DuckDB tells them apart: `"ä"` and
    `"Ä"` are different columns. The text of a constant (`literal`, or `value`
    before DuckDB 2.0) keeps its case; other keys of a constant, like its
    `alias`, don't.
    """
    if isinstance(obj, dict):
        is_constant = obj.get("class") == "CONSTANT"
        return {
            k: v if is_constant and k in ("literal", "value") else _fold_identifiers(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_fold_identifiers(v) for v in obj]
    if isinstance(obj, str):
        return obj.translate(_ASCII_LOWER)
    return obj


class DuckDBOracle(Oracle):
    """DuckDB's parser, through `json_serialize_sql`, which handles SELECTs.

    https://duckdb.org/docs/stable/data/json/sql_to_and_from_json
    """

    name = "duckdb"
    dialects = ("duckdb",)

    @classmethod
    def available(cls) -> bool:
        """Whether the `duckdb` package is installed."""
        try:
            import duckdb  # noqa: F401
        except ImportError:
            return False
        return True

    def __init__(self) -> None:
        import duckdb

        self._con = duckdb.connect()

    def tree(self, sql: str) -> Optional[str]:
        """Serialise a SELECT with DuckDB, without positions or identifier case."""
        try:
            (raw,) = self._con.execute("SELECT json_serialize_sql(?)", [sql]).fetchone()
        except Exception:  # pragma: no cover - defensive, the function returns errors
            return None
        result = json.loads(raw)
        if result.get("error"):
            return None
        statements = _drop_keys(
            result["statements"], lambda k, _: k.startswith("query_location")
        )
        return json.dumps(_fold_identifiers(statements), sort_keys=True)


@lru_cache(maxsize=1)
def _postgres_position_fields() -> frozenset[str]:
    """The node fields that PostgreSQL types as positions (`ParseLoc`).

    Read from pglast, so that fields added in new PostgreSQL versions, like the
    `list_start` and `rexpr_list_start` of PostgreSQL 18, are covered too.
    """
    import pglast.ast

    return frozenset(
        field
        for cls in vars(pglast.ast).values()
        if isinstance(getattr(cls, "__slots__", None), dict)
        for field, info in cls.__slots__.items()
        if getattr(info, "c_type", None) == "ParseLoc"
    )


class PostgresOracle(Oracle):
    """PostgreSQL's own parser, through pglast, which handles every statement.

    The parser lower-cases unquoted identifiers, as PostgreSQL does, so the tree
    needs no case folding.

    https://pglast.readthedocs.io/
    """

    name = "postgres"
    dialects = ("postgres",)

    @classmethod
    def available(cls) -> bool:
        """Whether the `pglast` package is installed."""
        try:
            import pglast  # noqa: F401
        except ImportError:
            return False
        return True

    def tree(self, sql: str) -> Optional[str]:
        """Parse a statement with PostgreSQL's parser, without positions."""
        import pglast

        try:
            result = json.loads(pglast.parser.parse_sql_json(sql))
        except pglast.parser.ParseError:
            return None
        positions = _postgres_position_fields()
        # A `location` can also be a string, like a tablespace's directory,
        # which is part of the statement, so only drop integers.
        statements = _drop_keys(
            result.get("stmts", []),
            lambda k, v: k in positions and isinstance(v, int),
        )
        return json.dumps(statements, sort_keys=True)


ORACLES: dict[str, type[Oracle]] = {
    cls.name: cls for cls in (DuckDBOracle, PostgresOracle)
}


@dataclass
class Stats:
    """How many statements a run saw, judged and fixed."""

    unparsable_files: int = 0
    statements: int = 0
    judged: int = 0
    changed: int = 0
    timeouts: int = 0
    errors: int = 0

    def add(self, other: Stats) -> None:
        """Add another worker's counts."""
        self.unparsable_files += other.unparsable_files
        self.statements += other.statements
        self.judged += other.judged
        self.changed += other.changed
        self.timeouts += other.timeouts
        self.errors += other.errors


@dataclass
class Failure:
    """A statement whose meaning a fix changed."""

    dialect: str
    fixture: str
    index: int
    original: str
    fixed: str
    reason: str
    rules: list[str] = field(default_factory=list)

    def matches(self, entry: dict[str, Any]) -> bool:
        """Whether a known-failures entry lists this failure."""
        return (
            entry["dialect"] == self.dialect
            and entry["fixture"] == self.fixture
            and self.original.startswith(entry["starts_with"])
        )


def _statements(sql: str, dialect: str) -> Optional[list[str]]:
    """The top-level statements of a fixture, or None if it doesn't parse."""
    linter = Linter(
        config=FluffConfig(overrides={"dialect": dialect, "templater": "raw"})
    )
    parsed = linter.parse_string(sql)
    if parsed.violations:
        return None
    try:
        tree = parsed.tree
    except AssertionError:  # pragma: no cover - e.g. the file doesn't lex
        return None
    if tree is None:  # pragma: no cover
        return None
    return [
        segment.raw for segment in tree.recursive_crawl("statement", recurse_into=False)
    ]


def _config(overrides: dict[str, Any], config_path: Optional[str]) -> FluffConfig:
    """A config from the overrides, on top of a config file if one is given."""
    if config_path:
        return FluffConfig.from_path(
            str(Path(config_path).resolve().parent),
            extra_config_path=config_path,
            overrides=overrides,
        )
    return FluffConfig(overrides=overrides)


def _fix(
    sql: str, dialect: str, rules: Optional[list[str]], config_path: Optional[str]
) -> str:
    """Fix one statement with the given rules, or all of them but the excluded."""
    overrides: dict[str, Any] = {"dialect": dialect, "templater": "raw"}
    if rules:
        overrides["rules"] = ",".join(rules)
    else:
        overrides["rules"] = "all"
        overrides["exclude_rules"] = ",".join(EXCLUDED_RULES)
    linter = Linter(config=_config(overrides, config_path))
    return linter.lint_string(sql, fix=True).fix_string()[0]


def _fixable_rules(sql: str, dialect: str, config_path: Optional[str]) -> list[str]:
    """The rules with a fix for this statement."""
    linter = Linter(
        config=_config(
            {
                "dialect": dialect,
                "templater": "raw",
                "rules": "all",
                "exclude_rules": ",".join(EXCLUDED_RULES),
            },
            config_path,
        )
    )
    violations = linter.lint_string(sql).violations
    return sorted({v.rule_code() for v in violations if getattr(v, "fixes", None)})


class _Timeout(BaseException):
    """The statement's time ran out.

    A BaseException, so that the `except Exception` blocks that skip one rule
    while naming the rules don't swallow it.
    """


def _raise_timeout(*_: Any) -> None:
    raise _Timeout()


def _check_statement(
    statement: str,
    dialect: str,
    oracle: Oracle,
    oracle_name: str,
    rules: Optional[list[str]],
    config_path: Optional[str],
) -> tuple[str, Optional[str], list[str]]:
    """Fix one statement and judge it.

    Returns the fixed statement, the reason if the fix changed what it means,
    and the rules whose fix changes the meaning on their own.
    """
    before = oracle.tree(statement)
    fixed = _fix(statement + "\n", dialect, rules, config_path).rstrip("\n")
    if fixed == statement:
        return fixed, None, []
    after = oracle.tree(fixed)
    if after == before:
        return fixed, None, []
    reason = (
        f"The {oracle_name} parser can't parse the fixed statement"
        if after is None
        else "The fix changes the syntax tree"
    )
    # Which rules change the meaning on their own? Each is tried separately, so
    # that one which can't fix the statement alone doesn't hide the others.
    culprits = []
    for rule in rules or _fixable_rules(statement + "\n", dialect, config_path):
        try:
            single = _fix(statement + "\n", dialect, [rule], config_path)
        except Exception:  # pragma: no cover - the full fix already worked
            continue
        single = single.rstrip("\n")
        if single != statement and oracle.tree(single) != before:
            culprits.append(rule)
    return fixed, reason, culprits


def _check_fixture(
    args: tuple[str, str, str, Optional[list[str]], Optional[str]],
) -> tuple[list[Failure], Stats, list[str]]:
    """Check every statement of one fixture. Runs in a worker process.

    Returns the failures, the counts, and the statements that were judged, so
    that a known failure is only reported as passing if it was judged.
    """
    path, dialect, oracle_name, rules, config_path = args
    oracle = ORACLES[oracle_name]()
    fixture = str(Path(path).relative_to(FIXTURES))
    failures: list[Failure] = []
    judged: list[str] = []
    stats = Stats()
    statements = _statements(Path(path).read_text(), dialect)
    if statements is None:
        stats.unparsable_files += 1
        return failures, stats, judged
    for index, statement in enumerate(statements):
        stats.statements += 1
        if oracle.tree(statement) is None:
            # The oracle can't judge this statement.
            continue
        # The timeout covers naming the rules too.
        if hasattr(signal, "SIGALRM"):
            signal.signal(signal.SIGALRM, _raise_timeout)
            signal.alarm(STATEMENT_TIMEOUT)
        try:
            fixed, reason, culprits = _check_statement(
                statement, dialect, oracle, oracle_name, rules, config_path
            )
        except _Timeout:
            stats.timeouts += 1
            continue
        except Exception:
            # e.g. the statement only parses as part of its file.
            stats.errors += 1
            continue
        finally:
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
        stats.judged += 1
        judged.append(statement)
        stats.changed += fixed != statement
        if reason:
            failures.append(
                Failure(
                    dialect=dialect,
                    fixture=fixture,
                    index=index,
                    original=statement,
                    fixed=fixed,
                    reason=reason,
                    rules=culprits,
                )
            )
    return failures, stats, judged


def _load_known_failures() -> list[dict[str, Any]]:
    """Read the known failures."""
    if not KNOWN_FAILURES.exists():
        return []  # pragma: no cover
    return yaml.safe_load(KNOWN_FAILURES.read_text()) or []


@dataclass
class DialectResult:
    """The outcome of checking one dialect."""

    dialect: str
    oracle: str
    checked: int
    stats: Stats
    new: list[Failure]
    known: list[Failure]
    now_pass: list[dict[str, Any]]


def _markdown(results: list[DialectResult]) -> str:
    """A report for a terminal or a CI step summary."""
    lines = [
        "# Fix safety",
        "",
        "A failure is a fix whose syntax tree differs from the original's, or that "
        "the database can't parse. It may change what the query means, and needs "
        "a look: two different trees can still mean the same thing.",
    ]
    for r in results:
        stats = r.stats
        lines += [
            "",
            f"## {r.dialect}, judged by the {r.oracle} parser",
            "",
            f"Checked {r.checked} fixture files, {stats.unparsable_files} of which "
            f"don't parse as a whole and are skipped: {stats.statements} "
            f"statements, {stats.judged} of which were judged. The fix changed "
            f"{stats.changed} of those. {stats.timeouts} timed out and "
            f"{stats.errors} couldn't be fixed on their own.",
            "",
            f"New failures: {len(r.new)}. Known failures: {len(r.known)}. "
            f"Known failures that now pass: {len(r.now_pass)}.",
        ]
        if stats.timeouts or stats.errors:
            lines += [
                "",
                "The run is incomplete: the statements that timed out or couldn't "
                "be fixed on their own weren't judged.",
            ]
        for title, items in (("New failures", r.new), ("Known failures", r.known)):
            if not items:
                continue
            lines += ["", f"### {title}"]
            for f in items:
                rules = ", ".join(f.rules) or "only when rules combine"
                lines += [
                    "",
                    f"#### `{f.fixture}`, statement {f.index}",
                    f"{f.reason}. Rules: {rules}.",
                    "",
                    "```sql",
                    f.original,
                    "```",
                    "",
                    "becomes",
                    "",
                    "```sql",
                    f.fixed,
                    "```",
                ]
        if r.now_pass:
            lines += ["", "### Known failures that now pass", ""]
            lines += [f"- `{e['fixture']}`: `{e['starts_with']}`" for e in r.now_pass]
    return "\n".join(lines) + "\n"


def _fixture_paths(dialect: str, args: argparse.Namespace) -> list[Path]:
    """The fixture files to check for a dialect."""
    return sorted(
        p
        for p in (FIXTURES / (args.fixtures or dialect)).glob("*.sql")
        if fnmatch.fnmatch(p.name, args.filter)
    )


def _check_dialect(
    dialect: str,
    oracle_name: str,
    args: argparse.Namespace,
    rules: Optional[list[str]],
) -> DialectResult:
    """Check one dialect's fixtures and compare with the known failures."""
    paths = _fixture_paths(dialect, args)
    jobs = [(str(p), dialect, oracle_name, rules, args.config) for p in paths]
    failures: list[Failure] = []
    judged: set[tuple[str, str]] = set()
    stats = Stats()
    results: list[tuple[list[Failure], Stats, list[str]]]
    if args.processes == 1:
        # In this process, which is easier to debug.
        results = [_check_fixture(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=args.processes) as pool:
            results = list(pool.map(_check_fixture, jobs))
    for path, (fixture_failures, fixture_stats, fixture_judged) in zip(paths, results):
        failures += fixture_failures
        stats.add(fixture_stats)
        fixture = str(path.relative_to(FIXTURES))
        judged |= {(fixture, statement) for statement in fixture_judged}

    entries = [e for e in _load_known_failures() if e["dialect"] == dialect]
    new = [f for f in failures if not any(f.matches(e) for e in entries)]
    known = [f for f in failures if any(f.matches(e) for e in entries)]
    # A known failure only passes if its statement was judged, with all rules
    # and the default settings, which is how it's listed.
    now_pass = []
    if not rules and not args.config:
        now_pass = [
            e
            for e in entries
            if any(
                fixture == e["fixture"] and statement.startswith(e["starts_with"])
                for fixture, statement in judged
            )
            and not any(f.matches(e) for f in failures)
        ]
    return DialectResult(dialect, oracle_name, len(paths), stats, new, known, now_pass)


def main(argv: Optional[list[str]] = None) -> int:
    """Run the check and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--dialect",
        action="append",
        required=True,
        help="Dialect to check. Repeat it to check several.",
    )
    parser.add_argument(
        "--oracle",
        help="Oracle to judge with. Defaults to the one for each dialect.",
    )
    parser.add_argument(
        "--rules", help="Comma-separated rules to fix with, instead of all."
    )
    parser.add_argument(
        "--filter", default="*", help="Glob for the fixture file names to check."
    )
    parser.add_argument(
        "--fixtures",
        help="Fixture folder to check, e.g. `ansi`. Defaults to the dialect's own.",
    )
    parser.add_argument(
        "--config",
        help="A .sqlfluff file with rule settings to fix with, e.g. other policies.",
    )
    parser.add_argument("--report", help="Also write the report to this file.")
    parser.add_argument(
        "--processes", type=int, default=os.cpu_count(), help="Worker processes."
    )
    args = parser.parse_args(argv)
    if args.processes < 1:
        parser.error("--processes must be at least 1")

    oracles = {}
    for dialect in args.dialect:
        oracle_name = args.oracle or next(
            (name for name, cls in ORACLES.items() if dialect in cls.dialects),
            None,
        )
        if oracle_name is None or oracle_name not in ORACLES:
            print(f"No oracle for the {dialect} dialect.", file=sys.stderr)
            return 2
        if not ORACLES[oracle_name].available():
            print(
                f"The {oracle_name} oracle isn't installed. "
                "Run `tox -e fix-safety` or install its package.",
                file=sys.stderr,
            )
            return 2
        oracles[dialect] = oracle_name

    for dialect in oracles:
        if not _fixture_paths(dialect, args):
            # e.g. a typo in `--filter` or `--fixtures`, which mustn't pass.
            print(
                f"No fixture files to check for the {dialect} dialect.",
                file=sys.stderr,
            )
            return 2

    rules = args.rules.split(",") if args.rules else None
    results = [
        _check_dialect(dialect, oracle_name, args, rules)
        for dialect, oracle_name in oracles.items()
    ]
    report = _markdown(results)
    print(report)
    if args.report:
        Path(args.report).write_text(report)
    if any(r.new or r.now_pass for r in results):
        return 1
    if any(r.stats.timeouts or r.stats.errors for r in results):
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
