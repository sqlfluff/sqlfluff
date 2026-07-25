"""SparkSQL dialect parser rejection tests.

Positive/valid-SQL cases belong in the SQL/YAML parse fixtures under
test/fixtures/dialects/sparksql/ per project convention.
"""

import pytest

from sqlfluff.core import Linter


def _parse_violations(sql: str) -> list:
    """Return PRS violations and unparsable nodes for sparksql input."""
    parsed = Linter(dialect="sparksql").parse_string(sql)
    violations: list = [v for v in parsed.violations if v.rule_code() == "PRS"]
    if parsed.tree:
        violations += list(parsed.tree.recursive_crawl("unparsable"))
    return violations


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "SET spark.sql.shuffle.partitions = 200\nDROP TABLE prod.customers;\n",
            id="set_missing_terminator_before_drop",
        ),
        pytest.param(
            "SET spark.sql.foo = bar\nSELECT 1 FROM t;\n",
            id="set_missing_terminator_before_select",
        ),
        pytest.param(
            "SET spark.sql.shuffle.partitions = 200\n"
            "INSERT INTO prod.audit SELECT * FROM staging;\n",
            id="set_missing_terminator_before_insert",
        ),
        pytest.param(
            "SET path = s3a://bucket/path\nDROP TABLE prod.customers;\n",
            id="set_opaque_missing_terminator_before_drop",
        ),
        pytest.param(
            "SET spark.sql.shuffle.partitions = 200\n"
            "LOAD DATA INPATH '/tmp/data' INTO TABLE prod.customers;\n",
            id="set_missing_terminator_before_load",
        ),
    ],
)
def test_set_without_terminator_does_not_absorb_next_statement(sql: str) -> None:
    """A SET line without ';' must not silently absorb the following statement."""
    assert _parse_violations(sql) != [], (
        f"Expected parse violations but got none for:\n{sql}"
    )
