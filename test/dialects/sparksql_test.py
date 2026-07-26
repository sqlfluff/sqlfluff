"""SparkSQL dialect parser rejection / boundary tests.

Positive/valid-SQL cases belong in the SQL/YAML parse fixtures under
test/fixtures/dialects/sparksql/ per project convention.
"""

import pytest

from sqlfluff.core import Linter


def _parse_violations(sql: str, dialect: str = "sparksql") -> list:
    """Return PRS violations and unparsable nodes."""
    parsed = Linter(dialect=dialect).parse_string(sql)
    violations: list = [v for v in parsed.violations if v.rule_code() == "PRS"]
    if parsed.tree:
        violations += list(parsed.tree.recursive_crawl("unparsable"))
    return violations


def _parses_cleanly(sql: str, dialect: str = "sparksql") -> bool:
    return _parse_violations(sql, dialect=dialect) == []


# Follow-on statements after a SET line with no semicolon. These must not be
# absorbed into the opaque SET value (regression for #8187 / earfman).
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


def test_set_same_line_follow_on_does_not_absorb_next_statement() -> None:
    """Whitespace is a statement boundary for opaque SET values too."""
    sql = "SET spark.sql.shuffle.partitions = 200 DROP TABLE prod.customers;\n"
    assert _parse_violations(sql) != [], (
        f"Expected parse violations but got none for:\n{sql}"
    )


@pytest.mark.parametrize(
    "sql",
    [
        # Opaque values that look like statement keywords must still parse.
        # A starter-keyword terminator list would reject these.
        pytest.param(
            "SET spark.sql.foo = values;\n",
            id="opaque_values_keyword",
        ),
        pytest.param(
            "SET spark.sql.foo = grant;\n",
            id="opaque_grant_keyword",
        ),
        pytest.param(
            "SET spark.sql.sources.partitionOverwriteMode = dynamic,static;\n",
            id="opaque_comma_list",
        ),
        pytest.param(
            "SET key = a-b;\n",
            id="opaque_hyphenated",
        ),
        pytest.param(
            "SET path = s3a://bucket/path/to/data;\n",
            id="opaque_uri",
        ),
        pytest.param(
            "SET c_date = CURRENT_DATE();\n",
            id="function_value",
        ),
    ],
)
def test_set_config_values_still_parse(sql: str) -> None:
    """Valid SET forms must keep parsing after the boundary redesign."""
    assert _parses_cleanly(sql), f"Expected clean parse for:\n{sql}"


@pytest.mark.parametrize(
    "follow_on",
    [
        pytest.param(
            "COMMENT ON TABLE prod.customers IS 'x';",
            id="comment_on",
        ),
        pytest.param(
            "DECLARE VARIABLE answer INT DEFAULT 42;",
            id="declare_variable",
        ),
    ],
)
def test_databricks_set_without_terminator_does_not_absorb_follow_on(
    follow_on: str,
) -> None:
    """Databricks follow-ons must not be absorbed (inherits NonCode boundary)."""
    sql = f"SET spark.sql.shuffle.partitions = 200\n{follow_on}\n"
    assert _parse_violations(sql, dialect="databricks") != [], (
        f"Expected parse violations but got none for:\n{sql}"
    )
