"""SparkSQL dialect tests outside the SQL/YAML parse fixtures.

Positive/valid-SQL cases belong in test/fixtures/dialects/sparksql/.
"""

import pytest

from sqlfluff.core import Linter


def _parses_cleanly(sql: str, dialect: str = "sparksql") -> bool:
    parsed = Linter(dialect=dialect).parse_string(sql)
    violations = [v for v in parsed.violations if v.rule_code() == "PRS"]
    if parsed.tree:
        violations += list(parsed.tree.recursive_crawl("unparsable"))
    return violations == []


def _set_value_raw(sql: str, dialect: str = "sparksql") -> str:
    """Return the raw text of the first set_config_value, if any."""
    parsed = Linter(dialect=dialect).parse_string(sql)
    assert parsed.tree is not None
    values = list(parsed.tree.recursive_crawl("set_config_value"))
    assert values, f"Expected a set_config_value in:\n{sql}"
    return values[0].raw


@pytest.mark.parametrize(
    "sql,expected_value",
    [
        pytest.param(
            "SET c_date = CURRENT_DATE();\n",
            "CURRENT_DATE()",
            id="function_value",
        ),
        pytest.param(
            "SET path = s3a://bucket/path/to/data;\n",
            "s3a://bucket/path/to/data",
            id="opaque_uri",
        ),
        pytest.param(
            "SET key = a-b;\n",
            "a-b",
            id="opaque_hyphenated",
        ),
        pytest.param(
            "SET spark.sql.sources.partitionOverwriteMode = dynamic,static;\n",
            "dynamic,static",
            id="opaque_comma_list",
        ),
        pytest.param(
            "SET key = foo bar;\n",
            "foo bar",
            id="opaque_spaced",
        ),
        pytest.param(
            "SET spark.sql.foo = values;\n",
            "values",
            id="opaque_values_keyword",
        ),
        pytest.param(
            "SET key = comment;\n",
            "comment",
            id="opaque_comment_keyword",
        ),
        pytest.param(
            "SET spark.sql.shuffle.partitions = 200; DROP TABLE prod.customers;\n",
            "200",
            id="semicolon_separates_same_line",
        ),
    ],
)
def test_set_config_values_parse(sql: str, expected_value: str) -> None:
    """Spark SET values: expressions, opaque payloads, semicolon boundaries."""
    assert _parses_cleanly(sql), f"Expected clean parse for:\n{sql}"
    assert _set_value_raw(sql) == expected_value


@pytest.mark.parametrize(
    "sql,expected_value",
    [
        pytest.param(
            "SET key = comment;\n",
            "comment",
            id="bare_comment",
        ),
        pytest.param(
            "SET key = declare;\n",
            "declare",
            id="bare_declare",
        ),
        pytest.param(
            "SET spark.sql.shuffle.partitions = 200; COMMENT ON TABLE t IS 'x';\n",
            "200",
            id="same_line_comment_on",
        ),
    ],
)
def test_databricks_set_config_values_parse(sql: str, expected_value: str) -> None:
    """Databricks inherits Spark SET values; bare keywords stay parsable."""
    assert _parses_cleanly(sql, dialect="databricks"), (
        f"Expected clean parse for:\n{sql}"
    )
    assert _set_value_raw(sql, dialect="databricks") == expected_value
