"""RF01 and dbt's BigQuery ``_dbt_max_partition`` variable."""

import re

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.errors import SQLLintError
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.templaters.base import TemplatedFile
from sqlfluff.rules.references.RF01 import Rule_RF01

# Rendered shape of a dbt BigQuery incremental filter: ref() and the
# is_incremental branch are already SQL, and _dbt_max_partition remains.
_INCREMENTAL_SQL = """
SELECT
    DATE(_dbt_max_partition) AS partition_date,
    DATE(`_DBT_MAX_PARTITION`) AS quoted_partition_date,
    missing.col,
    _dbt_max_partition.some_column,
    _dbt_other,
    _dbt_max_partition_extra
FROM events
WHERE EXISTS (
    SELECT 1
    FROM earlier
    WHERE earlier.id = events.id
        AND earlier.d >= DATE(_Dbt_Max_Partition)
)
"""

# ANSI has no backtick-quoted identifiers. Same references, valid for that dialect.
_ANSI_SQL = """
SELECT
    DATE(_dbt_max_partition),
    missing.col,
    _dbt_max_partition.some_column,
    _dbt_other
FROM events
WHERE EXISTS (
    SELECT 1
    FROM earlier
    WHERE earlier.id = events.id
        AND earlier.d >= DATE(_Dbt_Max_Partition)
)
"""

_UNRESOLVED = {
    "missing.col",
    "_dbt_max_partition.some_column",
    "_dbt_other",
    "_dbt_max_partition_extra",
}
_STRICT_WITHOUT_DBT = _UNRESOLVED | {
    "_dbt_max_partition",
    "_Dbt_Max_Partition",
    "`_DBT_MAX_PARTITION`",
}


def _config(dialect: str, templater: str, force_enable: bool) -> FluffConfig:
    """Return an RF01 config for ``templater``.

    ``FluffConfig`` instantiates the templater. The dbt plugin is not part of
    the core suite, and its ``process()`` path needs a project. RF01 only
    reads the templater name, so name that execution context after init.
    """
    config = FluffConfig(
        configs={
            "core": {
                "dialect": dialect,
                "templater": "raw" if templater == "dbt" else templater,
            },
            "rules": {"references.from": {"force_enable": force_enable}},
        },
        overrides={"rules": "RF01"},
    )
    if templater == "dbt":
        config._configs["core"]["templater"] = "dbt"
    return config


def _rule(force_enable: bool) -> Rule_RF01:
    """Load the real RF01 rule at this strictness."""
    pack = Linter(config=_config("bigquery", "raw", force_enable)).get_rulepack()
    rule = pack.rules[0]
    assert isinstance(rule, Rule_RF01)
    assert rule.code == "RF01"
    return rule


def _parsed(sql: str, dialect: str) -> tuple[BaseSegment, TemplatedFile, Dialect]:
    """Parse ``sql`` with the raw templater."""
    config = _config(dialect, "raw", True)
    parsed = Linter(config=config).parse_string(sql)
    assert parsed.violations == []
    variant = parsed.parsed_variants[0]
    assert variant.tree is not None
    return variant.tree, variant.templated_file, config.get("dialect_obj")


def _references(errors: list[SQLLintError]) -> set[str]:
    """Return the raw references RF01 rejected."""
    found = set()
    for error in errors:
        assert error.rule_code() == "RF01"
        match = re.fullmatch(
            r"Reference '(.*)' refers to table/view not found in the FROM clause "
            r"or found in ancestor statement\.",
            error.desc(),
        )
        assert match is not None
        found.add(match.group(1))
    return found


def _crawl(
    rule: Rule_RF01,
    tree: BaseSegment,
    templated_file: TemplatedFile,
    dialect_obj: Dialect,
    dialect: str,
    templater: str,
) -> set[str]:
    """Run one RF01 crawl and return the references it rejected."""
    errors, _, _, _ = rule.crawl(
        tree,
        dialect=dialect_obj,
        fix=False,
        templated_file=templated_file,
        ignore_mask=None,
        fname=None,
        config=_config(dialect, templater, rule.force_enable),
    )
    return _references(errors)


def _flagged(rule: Rule_RF01, sql: str, dialect: str, templater: str) -> set[str]:
    """Parse ``sql`` with the raw templater, then crawl RF01."""
    tree, templated_file, dialect_obj = _parsed(sql, dialect)
    return _crawl(rule, tree, templated_file, dialect_obj, dialect, templater)


def test_dbt_bigquery_partition_variable_resolves_when_strict() -> None:
    """Unqualified ``_dbt_max_partition`` is not an RF01 hit under dbt BigQuery.

    A correlated subquery sees the same variable. Unknown tables, a qualified
    ``_dbt_max_partition.some_column``, and other ``_dbt_*`` names still fail.
    """
    rule = _rule(force_enable=True)
    assert _flagged(rule, _INCREMENTAL_SQL, "bigquery", "dbt") == _UNRESOLVED


def test_partition_variable_keeps_prior_resolution() -> None:
    """Raw, jinja, other dialects, and the default exemption stay unchanged."""
    strict = _rule(force_enable=True)
    assert _flagged(strict, _INCREMENTAL_SQL, "bigquery", "raw") == _STRICT_WITHOUT_DBT
    assert (
        _flagged(strict, _INCREMENTAL_SQL, "bigquery", "jinja") == _STRICT_WITHOUT_DBT
    )

    ansi_raw = _flagged(strict, _ANSI_SQL, "ansi", "raw")
    ansi_dbt = _flagged(strict, _ANSI_SQL, "ansi", "dbt")
    assert ansi_raw == ansi_dbt
    assert "missing.col" in ansi_raw
    assert "_dbt_max_partition.some_column" in ansi_raw
    assert "_dbt_max_partition" not in ansi_raw

    relaxed = _rule(force_enable=False)
    assert _flagged(relaxed, _INCREMENTAL_SQL, "bigquery", "dbt") == set()
    assert _flagged(relaxed, _INCREMENTAL_SQL, "bigquery", "raw") == set()


def test_dbt_context_does_not_leak_between_crawls() -> None:
    """Consecutive crawls with another templater do not keep the dbt context."""
    rule = _rule(force_enable=True)
    tree, templated_file, dialect_obj = _parsed(_INCREMENTAL_SQL, "bigquery")
    # One rule instance and one parsed tree. A sticky flag on the rule would
    # make the raw/jinja crawls inherit the dbt result, or the second dbt
    # crawl inherit the raw result.
    assert (
        _crawl(rule, tree, templated_file, dialect_obj, "bigquery", "dbt")
        == _UNRESOLVED
    )
    assert (
        _crawl(rule, tree, templated_file, dialect_obj, "bigquery", "raw")
        == _STRICT_WITHOUT_DBT
    )
    assert (
        _crawl(rule, tree, templated_file, dialect_obj, "bigquery", "jinja")
        == _STRICT_WITHOUT_DBT
    )
    assert (
        _crawl(rule, tree, templated_file, dialect_obj, "bigquery", "dbt")
        == _UNRESOLVED
    )
