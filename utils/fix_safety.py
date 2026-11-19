#!/usr/bin/env python3
"""Check that `sqlfluff fix` doesn't change what a query means.

For each statement in a dialect's parse fixtures, this runs ``sqlfluff fix``
with every rule, then asks the real database's own parser, an *oracle*, for
the syntax tree of the statement before and after the fix. If the trees
differ, or the fixed statement no longer parses, the fix changed the query.

Each failure is then run again with one rule at a time, to name the rules
whose fix changes the query on its own.

Failures listed in ``utils/fix_safety_known_failures.yml`` are reported but
don't fail the run. Entries that no longer fail are reported too, so the list
can be kept up to date.

Exit codes: 0 when there are no new failures, 1 when there are new failures or
listed ones that pass, and 2 when the dialect has no oracle or it's missing.

Usage:
    python utils/fix_safety.py --dialect duckdb
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


def _fold_identifiers(obj: Any) -> Any:
    """Lower-case every string in a DuckDB tree except constant values.

    DuckDB resolves identifiers case-insensitively, quoted or not, but its
    serialised tree keeps the case they were written in. The text of a constant
    (`literal`, or `value` before DuckDB 2.0) keeps its case; other keys of a
    constant, like its `alias`, don't.
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
        return obj.lower()
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


class _Timeout(Exception):
    pass


def _raise_timeout(*_: Any) -> None:
    raise _Timeout()


def _check_fixture(
    args: tuple[str, str, str, Optional[list[str]], Optional[str]],
) -> tuple[list[Failure], Stats]:
    """Check every statement of one fixture. Runs in a worker process."""
    path, dialect, oracle_name, rules, config_path = args
    oracle = ORACLES[oracle_name]()
    fixture = str(Path(path).relative_to(FIXTURES))
    failures = []
    stats = Stats()
    statements = _statements(Path(path).read_text(), dialect)
    if statements is None:
        stats.unparsable_files += 1
        return failures, stats
    for index, statement in enumerate(statements):
        stats.statements += 1
        before = oracle.tree(statement)
        if before is None:
            # The oracle can't judge this statement.
            continue
        stats.judged += 1
        if hasattr(signal, "SIGALRM"):
            signal.signal(signal.SIGALRM, _raise_timeout)
            signal.alarm(STATEMENT_TIMEOUT)
        try:
            fixed = _fix(statement + "\n", dialect, rules, config_path).rstrip("\n")
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
        if fixed == statement:
            continue
        stats.changed += 1
        after = oracle.tree(fixed)
        if after == before:
            continue
        failure = Failure(
            dialect=dialect,
            fixture=fixture,
            index=index,
            original=statement,
            fixed=fixed,
            reason=(
                f"The {oracle_name} parser can't parse the fixed statement"
                if after is None
                else "The fix changes the syntax tree"
            ),
        )
        # Which rules change the meaning on their own?
        try:
            candidates = rules or _fixable_rules(statement + "\n", dialect, config_path)
            for rule in candidates:
                single = _fix(statement + "\n", dialect, [rule], config_path)
                single = single.rstrip("\n")
                if single != statement and oracle.tree(single) != before:
                    failure.rules.append(rule)
        except Exception:  # pragma: no cover - the full fix already worked
            pass
        failures.append(failure)
    return failures, stats


def _load_known_failures() -> list[dict[str, Any]]:
    """Read the known failures."""
    if not KNOWN_FAILURES.exists():
        return []  # pragma: no cover
    return yaml.safe_load(KNOWN_FAILURES.read_text()) or []


def _markdown(
    new: list[Failure],
    known: list[Failure],
    fixed: list[dict[str, Any]],
    checked: int,
    stats: Stats,
    oracle: str,
) -> str:
    """A report for a terminal or a CI step summary."""
    lines = [
        f"# Fix safety: {oracle}",
        "",
        f"Checked {checked} fixture files, {stats.unparsable_files} of which "
        f"don't parse as a whole and are skipped: {stats.statements} statements, "
        f"{stats.judged} of which {oracle} can judge. The fix changed "
        f"{stats.changed} of those. {stats.timeouts} timed out and "
        f"{stats.errors} couldn't be fixed on their own.",
        f"New failures: {len(new)}. Known failures: {len(known)}. "
        f"Known failures that now pass: {len(fixed)}.",
    ]
    for title, items in (("New failures", new), ("Known failures", known)):
        if not items:
            continue
        lines += ["", f"## {title}"]
        for f in items:
            rules = ", ".join(f.rules) or "only when rules combine"
            lines += [
                "",
                f"### `{f.fixture}`, statement {f.index}",
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
    if fixed:
        lines += ["", "## Known failures that now pass", ""]
        lines += [
            f"- `{e['fixture']}` as {e['dialect']}: `{e['starts_with']}`" for e in fixed
        ]
    return "\n".join(lines) + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    """Run the check and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dialect", required=True, help="Dialect to check.")
    parser.add_argument(
        "--oracle",
        help="Oracle to judge with. Defaults to the one for the dialect.",
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

    oracle_name = args.oracle or next(
        (name for name, cls in ORACLES.items() if args.dialect in cls.dialects),
        None,
    )
    if oracle_name is None or oracle_name not in ORACLES:
        print(f"No oracle for the {args.dialect} dialect.", file=sys.stderr)
        return 2
    if not ORACLES[oracle_name].available():
        print(
            f"The {oracle_name} oracle isn't installed. "
            "Run `tox -e fix-safety` or install its package.",
            file=sys.stderr,
        )
        return 2

    rules = args.rules.split(",") if args.rules else None
    paths = sorted(
        p
        for p in (FIXTURES / (args.fixtures or args.dialect)).glob("*.sql")
        if fnmatch.fnmatch(p.name, args.filter)
    )
    jobs = [(str(p), args.dialect, oracle_name, rules, args.config) for p in paths]
    failures: list[Failure] = []
    stats = Stats()
    with ProcessPoolExecutor(max_workers=args.processes) as pool:
        for fixture_failures, fixture_stats in pool.map(_check_fixture, jobs):
            failures += fixture_failures
            stats.add(fixture_stats)

    entries = _load_known_failures()
    checked_fixtures = {str(p.relative_to(FIXTURES)) for p in paths}
    new = [f for f in failures if not any(f.matches(e) for e in entries)]
    known = [f for f in failures if any(f.matches(e) for e in entries)]
    # Only judge known failures for fixtures this run checked, with all rules
    # and the default settings, which is how they're listed.
    now_pass = [
        e
        for e in entries
        if not rules
        and not args.config
        and e["dialect"] == args.dialect
        and e["fixture"] in checked_fixtures
        and not any(f.matches(e) for f in failures)
    ]

    report = _markdown(new, known, now_pass, len(paths), stats, oracle_name)
    print(report)
    if args.report:
        Path(args.report).write_text(report)
    return 1 if new or now_pass else 0


if __name__ == "__main__":
    sys.exit(main())
