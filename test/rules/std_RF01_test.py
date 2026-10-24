"""Tests for RF01 execution-context implicit references."""

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize(
    "dialect,sql,dbt_references,other_references",
    [
        (
            "bigquery",
            """SELECT t.id, item
            FROM events AS t
            CROSS JOIN UNNEST(t.items) AS item
            WHERE DATE(t.created_at) >= DATE(_dbt_max_partition)
                AND DATE(t.created_at) >= DATE(_DBT_MAX_PARTITION)
                AND DATE(t.created_at) >= DATE(_Dbt_Max_Partition)""",
            [],
            ["_dbt_max_partition", "_DBT_MAX_PARTITION", "_Dbt_Max_Partition"],
        ),
        (
            "bigquery",
            """WITH recent AS (
                SELECT t.id FROM events AS t
                WHERE DATE(t.created_at) >= DATE(_dbt_max_partition)
            )
            SELECT r.id FROM recent AS r
            WHERE r.id IN (
                SELECT e.id FROM events AS e
                WHERE DATE(e.created_at) >= DATE(_Dbt_Max_Partition)
                    AND e.id = missing.id
            )""",
            ["missing.id"],
            ["_dbt_max_partition", "_Dbt_Max_Partition", "missing.id"],
        ),
        (
            "bigquery",
            "SELECT DATE(_dbt_other_partition) FROM events",
            ["_dbt_other_partition"],
            ["_dbt_other_partition"],
        ),
        (
            "postgres",
            "SELECT _dbt_max_partition.value FROM events",
            ["_dbt_max_partition.value"],
            ["_dbt_max_partition.value"],
        ),
    ],
)
def test_rf01_dbt_bigquery_context(
    dialect: str,
    sql: str,
    dbt_references: list[str],
    other_references: list[str],
) -> None:
    """Only dbt BigQuery supplies the exact variable, without leaking state."""
    config = FluffConfig(
        configs={"rules": {"references.from": {"force_enable": True}}},
        overrides={"dialect": dialect, "templater": "raw", "rules": "RF01"},
    )
    linter = Linter(config=config)
    parsed = linter.parse_string(sql)
    assert not parsed.violations
    assert parsed.tree is not None
    assert not list(parsed.tree.recursive_crawl("unparsable"))
    rule = linter.get_rulepack(config=config).rules[0]
    assert rule.code == "RF01"

    # Reuse the same rule across contexts, without loading the dbt plugin.
    for templater in ("dbt", "raw", "jinja", "dbt"):
        config.set_value(["core", "templater"], templater)
        errors, _, _, _ = rule.crawl(
            parsed.tree,
            dialect=config.get("dialect_obj"),
            fix=False,
            templated_file=parsed.parsed_variants[0].templated_file,
            ignore_mask=None,
            fname="<string>",
            config=config,
        )
        references = dbt_references if templater == "dbt" else other_references
        assert [error.rule_code() for error in errors] == ["RF01"] * len(references)
        assert [error.description for error in errors] == [
            f"Reference {reference!r} refers to table/view "
            "not found in the FROM clause or found in ancestor statement."
            for reference in references
        ]
