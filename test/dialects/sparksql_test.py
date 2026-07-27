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


def _set_value_raw(sql: str, dialect: str = "sparksql") -> str:
    """Return the raw text of the first set_config_value, if any."""
    parsed = Linter(dialect=dialect).parse_string(sql)
    assert parsed.tree is not None
    values = list(parsed.tree.recursive_crawl("set_config_value"))
    assert values, f"Expected a set_config_value in:\n{sql}"
    return values[0].raw


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
    # Boundary is the newline: the SET value must stop before the follow-on.
    assert _set_value_raw(sql) == set_line.split(" = ", 1)[1]
    # Missing ';' between statements still surfaces as a parse problem.
    assert _parse_violations(sql) != [], (
        f"Expected parse violations but got none for:\n{sql}"
    )


def test_set_same_line_semicolon_separates_statements() -> None:
    """Same-line follow-ons are fine when separated by a real terminator."""
    sql = "SET spark.sql.shuffle.partitions = 200; DROP TABLE prod.customers;\n"
    assert _parses_cleanly(sql), f"Expected clean parse for:\n{sql}"
    assert _set_value_raw(sql) == "200"


@pytest.mark.parametrize(
    "sql,expected_value",
    [
        # Opaque values that look like statement keywords must still parse.
        # A starter-keyword terminator list would reject these.
        pytest.param(
            "SET spark.sql.foo = values;\n",
            "values",
            id="opaque_values_keyword",
        ),
        pytest.param(
            "SET spark.sql.foo = grant;\n",
            "grant",
            id="opaque_grant_keyword",
        ),
        pytest.param(
            "SET key = comment;\n",
            "comment",
            id="opaque_comment_keyword",
        ),
        pytest.param(
            "SET key = declare;\n",
            "declare",
            id="opaque_declare_keyword",
        ),
        pytest.param(
            "SET spark.sql.sources.partitionOverwriteMode = dynamic,static;\n",
            "dynamic,static",
            id="opaque_comma_list",
        ),
        pytest.param(
            "SET key = a-b;\n",
            "a-b",
            id="opaque_hyphenated",
        ),
        pytest.param(
            "SET path = s3a://bucket/path/to/data;\n",
            "s3a://bucket/path/to/data",
            id="opaque_uri",
        ),
        # Intra-line spaces are part of the opaque value, not a boundary.
        pytest.param(
            "SET key = foo bar;\n",
            "foo bar",
            id="opaque_spaced",
        ),
        pytest.param(
            "SET c_date = CURRENT_DATE();\n",
            "CURRENT_DATE()",
            id="function_value",
        ),
    ],
)
def test_set_config_values_still_parse(sql: str, expected_value: str) -> None:
    """Valid SET forms must keep parsing after the boundary redesign."""
    assert _parses_cleanly(sql), f"Expected clean parse for:\n{sql}"
    assert _set_value_raw(sql) == expected_value


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
    """Databricks newline follow-ons must not be absorbed (newline boundary)."""
    sql = f"SET spark.sql.shuffle.partitions = 200\n{follow_on}\n"
    assert _set_value_raw(sql, dialect="databricks") == "200"
    assert _parse_violations(sql, dialect="databricks") != [], (
        f"Expected parse violations but got none for:\n{sql}"
    )


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
def test_databricks_set_bare_keyword_values_and_same_line_follow_on(
    sql: str, expected_value: str
) -> None:
    """Bare keyword values and semicolon-separated same-line follow-ons."""
    assert _parses_cleanly(sql, dialect="databricks"), (
        f"Expected clean parse for:\n{sql}"
    )
    assert _set_value_raw(sql, dialect="databricks") == expected_value
