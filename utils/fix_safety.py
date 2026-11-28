#!/usr/bin/env python3
"""Flag fixes that may change what a query means, for review.

For each statement in a dialect's parse fixtures, this runs ``sqlfluff fix``
and asks the database's own parser, an *oracle*, for the statement's syntax
tree before and after the fix. If the trees differ, or the database can't parse
the fixed statement, the fix is flagged, and the statement is fixed again with
one rule at a time to try to name the rules that did it.

A flagged fix needs a person to look at it: two different trees can still mean
the same thing. And a fix that isn't flagged isn't proven safe. The check only
sees:

- the statements in the fixtures, each on its own and without templating;
- the rules it fixes with, and their settings (see below);
- what the oracle's parser keeps: comments aren't in either tree, and DuckDB's
  ``json_serialize_sql`` only handles SELECTs.

Rules: with ``--rules``, the check fixes with exactly those rules. Otherwise it
fixes with every rule, or with the ``rules`` and ``exclude_rules`` of the
``--config`` file. The rule settings are the defaults, or those of
``--config``, which is the only config file read.

Known failures: ``utils/fix_safety_known_failures.yml`` lists the fixes that a
default run, without ``--rules`` and ``--config``, flags, each with the reason
a person gave after looking at it: a rewrite whose change is meant, like ST06
reordering the columns of a SELECT, or a bug to fix. In a default run, listed
fixes don't fail the check, and a listed statement that's judged and passes
does, so the list stays current. With ``--rules`` or ``--config``, the list
isn't used, and every flagged fix fails the check.

Exit codes:
    1: a fix was flagged that isn't listed, or, in a default run, a listed
       statement passes.
    2: the check couldn't judge all it should: a dialect has no oracle or its
       oracle isn't installed, no fixture file matches, a fixture file
       couldn't be parsed, fixing a statement raised or timed out (after 30
       seconds, where there's SIGALRM, i.e. not on Windows), or the oracle
       could judge none of a dialect's statements. Usage errors and unexpected
       errors exit with 2 too.
    0: neither.
When both 1 and 2 apply, the exit code is 1.

Usage:
    python utils/fix_safety.py --dialect duckdb --dialect postgres
    python utils/fix_safety.py --dialect postgres --filter "create_function*"
    python utils/fix_safety.py --dialect postgres --rules CV11 --config my.sqlfluff

The oracles need their database's parser installed (``duckdb``, ``pglast``);
the ``fix-safety`` tox environment installs them.
"""

from __future__ import annotations

import argparse
import copy
import fnmatch
import json
import os
import signal
import sys
import traceback
from collections.abc import Callable, Iterator
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import yaml

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.config.loader import load_config_file
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.rules import get_ruleset

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "test" / "fixtures" / "dialects"
KNOWN_FAILURES = Path(__file__).resolve().parent / "fix_safety_known_failures.yml"


# Seconds allowed for splitting a fixture into statements, and for fixing and
# judging one statement. The time limit uses SIGALRM, so it only applies where
# there is one, i.e. not on Windows.
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

    files: int = 0
    unparsable_files: int = 0
    statements: int = 0
    judged: int = 0
    changed: int = 0
    timeouts: int = 0
    errors: int = 0

    def add(self, other: Stats) -> None:
        """Add another fixture's counts."""
        for name in vars(self):
            setattr(self, name, getattr(self, name) + getattr(other, name))

    def incomplete(self) -> list[str]:
        """Why the run is incomplete, if it is."""
        reasons = []
        if self.unparsable_files:
            reasons.append(f"{self.unparsable_files} fixture files couldn't be parsed")
        if self.timeouts:
            reasons.append(f"{self.timeouts} statements timed out")
        if self.errors:
            reasons.append(f"fixing {self.errors} statements raised an error")
        if not self.judged:
            reasons.append("the oracle could judge none of the statements")
        return reasons


@dataclass
class Failure:
    """A statement whose fix may change what it means."""

    dialect: str
    fixture: str
    number: int
    original: str
    fixed: str
    reason: str
    rules: list[str] = field(default_factory=list)
    # Why it's listed as a known failure, if it is.
    listed_reason: str = ""

    def matches(self, entry: dict[str, str]) -> bool:
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
    if parsed.violations or parsed.tree is None:
        return None
    return [
        segment.raw
        for segment in parsed.tree.recursive_crawl("statement", recurse_into=False)
    ]


@lru_cache(maxsize=None)
def _file_configs(config_path: Optional[str]) -> dict[str, Any]:
    """The values of the `--config` file, and only that file."""
    if not config_path:
        return {}
    path = Path(config_path)
    return load_config_file(str(path.parent), path.name)


def _config(overrides: dict[str, Any], config_path: Optional[str]) -> FluffConfig:
    """A config of the overrides, on top of the `--config` file if there's one."""
    return FluffConfig(
        configs=copy.deepcopy(_file_configs(config_path)), overrides=overrides
    )


@lru_cache(maxsize=None)
def _file_selection(config_path: Optional[str]) -> tuple[str, Optional[str]]:
    """The `rules` and `exclude_rules` of the `--config` file, or the defaults."""
    file_config = FluffConfig(
        configs=copy.deepcopy(_file_configs(config_path)), require_dialect=False
    )
    return file_config.get("rules") or "all", file_config.get("exclude_rules")


def _selection(
    rules: Optional[list[str]], config_path: Optional[str]
) -> dict[str, str]:
    """The `rules` and `exclude_rules` to fix with (see the module docstring)."""
    if rules:
        # Exactly these, whatever the `--config` file excludes.
        return {"rules": ",".join(rules), "exclude_rules": ""}
    selected, excluded = _file_selection(config_path)
    return {"rules": selected, "exclude_rules": excluded or ""}


def _overrides(
    dialect: str, rules: Optional[list[str]], config_path: Optional[str]
) -> dict[str, Any]:
    """The config overrides to fix one statement with."""
    return {"dialect": dialect, "templater": "raw", **_selection(rules, config_path)}


def _fix(
    sql: str, dialect: str, rules: Optional[list[str]], config_path: Optional[str]
) -> str:
    """Fix one statement with the selected rules."""
    linter = Linter(
        config=_config(_overrides(dialect, rules, config_path), config_path)
    )
    return linter.lint_string(sql, fix=True).fix_string()[0]


def _fixable_rules(sql: str, dialect: str, config_path: Optional[str]) -> list[str]:
    """The selected rules with a fix for this statement."""
    linter = Linter(config=_config(_overrides(dialect, None, config_path), config_path))
    violations = linter.lint_string(sql).violations
    return sorted({v.rule_code() for v in violations if getattr(v, "fixes", None)})


class _Timeout(BaseException):
    """The statement's time ran out.

    A BaseException, so that the `except Exception` blocks that skip one rule
    while naming the rules don't swallow it.
    """


def _raise_timeout(*_: Any) -> None:
    raise _Timeout()


@contextmanager
def _time_limit(seconds: int) -> Iterator[None]:
    """Raise `_Timeout` after `seconds`, where there's SIGALRM."""
    if not hasattr(signal, "SIGALRM"):
        yield
        return
    previous = signal.signal(signal.SIGALRM, _raise_timeout)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def _check_statement(
    statement: str,
    dialect: str,
    oracle: Oracle,
    oracle_name: str,
    rules: Optional[list[str]],
    config_path: Optional[str],
) -> tuple[str, Optional[str], list[str]]:
    """Fix one statement and judge it.

    Returns the fixed statement, the reason if the fix may change what it
    means, and the rules whose fix does on its own.
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
    # Which rules do it on their own? Each is tried separately, so that one
    # which can't fix the statement alone doesn't hide the others.
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
    that a listed statement is only reported as passing if it was judged.
    """
    path, dialect, oracle_name, rules, config_path = args
    oracle = ORACLES[oracle_name]()
    fixture = Path(path).relative_to(FIXTURES).as_posix()
    failures: list[Failure] = []
    judged: list[str] = []
    stats = Stats(files=1)
    try:
        with _time_limit(STATEMENT_TIMEOUT):
            statements = _statements(Path(path).read_text(encoding="utf-8"), dialect)
    except (Exception, _Timeout):
        statements = None
    if statements is None:
        stats.unparsable_files += 1
        return failures, stats, judged
    for number, statement in enumerate(statements, start=1):
        stats.statements += 1
        try:
            # The time limit covers naming the rules too.
            with _time_limit(STATEMENT_TIMEOUT):
                if oracle.tree(statement) is None:
                    # The oracle can't judge this statement.
                    continue
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
        stats.judged += 1
        judged.append(statement)
        stats.changed += fixed != statement
        if reason:
            failures.append(
                Failure(dialect, fixture, number, statement, fixed, reason, culprits)
            )
    return failures, stats, judged


def _load_known_failures() -> list[dict[str, str]]:
    """Read the known failures, checking that each names a statement."""
    entries = yaml.safe_load(KNOWN_FAILURES.read_text(encoding="utf-8")) or []
    keys = ("dialect", "fixture", "starts_with", "reason")
    if not isinstance(entries, list) or not all(
        isinstance(entry, dict)
        and all(isinstance(entry.get(key), str) and entry[key] for key in keys)
        for entry in entries
    ):
        raise ValueError(
            f"Each entry of {KNOWN_FAILURES.name} needs a dialect, a fixture, "
            "a starts_with and a reason."
        )
    return entries


@dataclass
class DialectResult:
    """The outcome of checking one dialect."""

    dialect: str
    oracle: str
    stats: Stats
    new: list[Failure]
    known: list[Failure]
    now_pass: list[dict[str, str]]
    uses_known_failures: bool


def _markdown(results: list[DialectResult]) -> str:
    """A report for a terminal or a CI step summary."""
    lines = [
        "# Fix safety",
        "",
        "A flagged fix is one whose syntax tree differs from the original's, or "
        "that the database can't parse. It may change what the query means, and "
        "needs a look: two different trees can still mean the same thing.",
    ]
    for r in results:
        stats = r.stats
        lines += [
            "",
            f"## {r.dialect}, judged by the {r.oracle} parser",
            "",
            f"Checked {stats.files} fixture files: {stats.statements} statements, "
            f"{stats.judged} of which were judged. The fix changed {stats.changed} "
            "of those.",
            "",
            f"Flagged fixes that aren't listed: {len(r.new)}. Listed: "
            f"{len(r.known)}. Listed statements that pass: {len(r.now_pass)}.",
        ]
        if not r.uses_known_failures:
            lines += [
                "",
                "The known failures aren't used, because `--rules` or `--config` "
                "was given.",
            ]
        reasons = stats.incomplete()
        if reasons:
            lines += ["", f"Not all was judged: {'; '.join(reasons)}."]
        if not hasattr(signal, "SIGALRM"):
            lines += [
                "",
                "There's no SIGALRM on this platform, so statements weren't "
                f"given a {STATEMENT_TIMEOUT}-second time limit.",
            ]
        if r.known:
            lines += ["", "### Listed fixes", ""]
            lines += [
                f"- `{f.fixture}`, statement {f.number} "
                f"({', '.join(f.rules) or 'rules combined'}): {f.listed_reason}"
                for f in r.known
            ]
        if r.new:
            lines += ["", "### Flagged fixes"]
            for f in r.new:
                rules = ", ".join(f.rules) or "only when rules combine"
                lines += [
                    "",
                    f"#### `{f.fixture}`, statement {f.number}",
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
            lines += ["", "### Listed statements that pass", ""]
            lines += [f"- `{e['fixture']}`: `{e['starts_with']}`" for e in r.now_pass]
    return "\n".join(lines) + "\n"


def _fixture_paths(dialect: str, pattern: str) -> list[Path]:
    """The fixture files to check for a dialect."""
    return sorted(
        p
        for p in (FIXTURES / dialect).glob("*.sql")
        if fnmatch.fnmatch(p.name, pattern)
    )


def _check_dialect(
    dialect: str,
    oracle_name: str,
    args: argparse.Namespace,
    rules: Optional[list[str]],
    known_failures: Optional[list[dict[str, str]]],
) -> DialectResult:
    """Check one dialect's fixtures and compare them with the known failures."""
    paths = _fixture_paths(dialect, args.filter)
    jobs = [(str(p), dialect, oracle_name, rules, args.config) for p in paths]
    results: list[tuple[list[Failure], Stats, list[str]]]
    if args.processes == 1:
        # In this process, which is easier to debug.
        results = [_check_fixture(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=args.processes) as pool:
            results = list(pool.map(_check_fixture, jobs))

    failures: list[Failure] = []
    judged: set[tuple[str, str]] = set()
    stats = Stats()
    for path, (fixture_failures, fixture_stats, fixture_judged) in zip(paths, results):
        failures += fixture_failures
        stats.add(fixture_stats)
        fixture = path.relative_to(FIXTURES).as_posix()
        judged |= {(fixture, statement) for statement in fixture_judged}

    entries = [e for e in known_failures or [] if e["dialect"] == dialect]
    new, known = [], []
    for f in failures:
        entry = next((e for e in entries if f.matches(e)), None)
        if entry is None:
            new.append(f)
        else:
            f.listed_reason = entry["reason"]
            known.append(f)
    # A listed statement only passes if it was judged.
    now_pass = [
        e
        for e in entries
        if any(
            fixture == e["fixture"] and statement.startswith(e["starts_with"])
            for fixture, statement in judged
        )
        and not any(f.matches(e) for f in failures)
    ]
    return DialectResult(
        dialect, oracle_name, stats, new, known, now_pass, known_failures is not None
    )


def _unknown_rules(rules: list[str]) -> list[str]:
    """The rules that match no rule sqlfluff knows.

    sqlfluff only warns about an unknown rule, so a typo would pass. Like
    sqlfluff, this matches each rule as a glob of rule references, without
    regard to case, e.g. `lt01` or `LT*`.
    """
    references = [ref.lower() for ref in get_ruleset().rule_reference_map()]
    return [
        rule
        for rule in rules
        if not any(fnmatch.fnmatchcase(ref, rule.lower()) for ref in references)
    ]


def _split_rules(rules: Optional[str]) -> list[str]:
    """The rules of a comma-separated list, without spaces or empty items."""
    return [rule.strip() for rule in (rules or "").split(",") if rule.strip()]


def _parse_args(
    argv: Optional[list[str]],
) -> tuple[argparse.Namespace, Optional[list[str]]]:
    """Parse and check the options, and return them with the rules to fix with."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--dialect",
        action="append",
        required=True,
        help="Dialect to check. Repeat it to check several.",
    )
    parser.add_argument("--rules", help="Comma-separated rules to fix with.")
    parser.add_argument(
        "--filter", default="*", help="Glob for the fixture file names to check."
    )
    parser.add_argument(
        "--config",
        help="A .sqlfluff file of the rule settings and rules to fix with.",
    )
    parser.add_argument(
        "--processes",
        type=int,
        # cpu_count() is None when the number of CPUs can't be told.
        default=os.cpu_count() or 1,
        help="Worker processes. With 1, the check runs in this process.",
    )
    args = parser.parse_args(argv)
    if args.processes < 1:
        parser.error("--processes must be at least 1")
    if args.config:
        # A quoted `~` isn't expanded by the shell.
        args.config = str(Path(args.config).expanduser().resolve())
        if not Path(args.config).is_file():
            parser.error(f"--config {args.config} isn't a file")
        try:
            selected, excluded = _file_selection(args.config)
        except SQLFluffUserError as error:
            parser.error(f"--config: {error}")
        unknown = _unknown_rules(_split_rules(selected) + _split_rules(excluded))
        if unknown:
            parser.error(f"--config has unknown rules: {', '.join(unknown)}")
    rules = None
    if args.rules is not None:
        rules = _split_rules(args.rules)
        if not rules:
            parser.error("--rules names no rule")
        unknown = _unknown_rules(rules)
        if unknown:
            parser.error(f"--rules has unknown rules: {', '.join(unknown)}")
    return args, rules


def _run(argv: Optional[list[str]]) -> int:
    """Run the check; `main` adds the exit code for unexpected errors."""
    args, rules = _parse_args(argv)
    oracles = {}
    for dialect in args.dialect:
        oracle_name = next(
            (name for name, cls in ORACLES.items() if dialect in cls.dialects), None
        )
        if oracle_name is None:
            print(f"No oracle for the {dialect} dialect.", file=sys.stderr)
            return 2
        if not ORACLES[oracle_name].available():
            print(
                f"The {oracle_name} oracle isn't installed. "
                "Run `tox -e fix-safety` or install its package.",
                file=sys.stderr,
            )
            return 2
        if not _fixture_paths(dialect, args.filter):
            # e.g. a typo in `--filter`, which mustn't pass.
            print(
                f"No fixture files to check for the {dialect} dialect.", file=sys.stderr
            )
            return 2
        oracles[dialect] = oracle_name

    # The known failures are those of a default run.
    known_failures = None if rules or args.config else _load_known_failures()
    results = [
        _check_dialect(dialect, oracle_name, args, rules, known_failures)
        for dialect, oracle_name in oracles.items()
    ]
    print(_markdown(results), end="")
    if any(r.new or r.now_pass for r in results):
        return 1
    if any(r.stats.incomplete() for r in results):
        return 2
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Run the check and return the exit code (see the module docstring)."""
    try:
        return _run(argv)
    except Exception:
        # Not 1, which means a fix was flagged.
        traceback.print_exc()
        return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
