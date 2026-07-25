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


# Representative next-statement bodies after a SET line with no semicolon.
# Cover the keywords cubic/humans have already caught missing, plus a few
# more StatementSegment starters so we do not regress one keyword at a time.
_SET_FOLLOWED_BY = [
    pytest.param("DROP TABLE prod.customers;", id="drop"),
    pytest.param("SELECT 1 FROM t;", id="select"),
    pytest.param(
        "INSERT INTO prod.audit SELECT * FROM staging;",
        id="insert",
    ),
    pytest.param(
        "LOAD DATA INPATH '/tmp/data' INTO TABLE prod.customers;",
        id="load",
    ),
    pytest.param(
        "CONSTRAINT c EXPECT (1 = 1);",
        id="constraint",
    ),
    pytest.param("GRANT SELECT ON TABLE t TO u;", id="grant"),
    pytest.param("REVOKE SELECT ON TABLE t FROM u;", id="revoke"),
    pytest.param("VALUES 1, 2;", id="values"),
    pytest.param("REPLACE TABLE t AS SELECT 1;", id="replace"),
]


@pytest.mark.parametrize("follow_on", _SET_FOLLOWED_BY)
@pytest.mark.parametrize(
    "set_line",
    [
        pytest.param(
            "SET spark.sql.shuffle.partitions = 200",
            id="literal_value",
        ),
        pytest.param(
            "SET path = s3a://bucket/path",
            id="opaque_value",
        ),
    ],
)
def test_set_without_terminator_does_not_absorb_next_statement(
    set_line: str, follow_on: str
) -> None:
    """A SET line without ';' must not silently absorb the following statement."""
    sql = f"{set_line}\n{follow_on}\n"
    assert _parse_violations(sql) != [], (
        f"Expected parse violations but got none for:\n{sql}"
    )
