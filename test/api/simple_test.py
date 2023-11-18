"""Tests for simple use cases of the public api."""

import json

import pytest

import sqlfluff
from sqlfluff.core.errors import SQLFluffUserError

my_bad_query = "SeLEct  *, 1, blah as  fOO  from myTable"

lint_result = [
    {
        "code": "AM04",
        "description": "Query produces an unknown number of result columns.",
        "line_no": 1,
        "line_pos": 1,
        "name": "ambiguous.column_count",
        "fixes": [],
        "warning": False,
        "source_position": (0, 40),
    },
    {
        "code": "CP01",
        "line_no": 1,
        "line_pos": 1,
        "description": "Keywords must be consistently upper case.",
        "name": "capitalisation.keywords",
        "fixes": [{"type": "replace", "edit": "SELECT", "source_position": (0, 6)}],
        "warning": False,
        "source_position": (0, 6),
    },
    {
        "code": "LT09",
        "description": "Select targets should be on a new line unless there is only "
        "one select target.",
        "line_no": 1,
        "line_pos": 1,
        "name": "layout.select_targets",
        "fixes": [
            {"type": "delete", "edit": "", "source_position": (6, 8)},
            {"type": "create_before", "edit": "\n", "source_position": (8, 9)},
            {"type": "delete", "edit": "", "source_position": (10, 11)},
            {"type": "create_before", "edit": "\n", "source_position": (11, 12)},
            {"type": "delete", "edit": "", "source_position": (13, 14)},
            {"type": "create_before", "edit": "\n", "source_position": (14, 26)},
            {"type": "delete", "edit": "", "source_position": (26, 28)},
            {"type": "create_before", "edit": "\n", "source_position": (28, 40)},
        ],
        "warning": False,
        "source_position": (0, 26),
    },
    {
        "code": "LT01",
        "description": "Expected only single space before star '*'. Found '  '.",
        "line_no": 1,
        "line_pos": 7,
        "name": "layout.spacing",
        "fixes": [{"type": "replace", "edit": " ", "source_position": (6, 8)}],
        "warning": False,
        "source_position": (6, 8),
    },
    {
        "code": "AL03",
        "line_no": 1,
        "line_pos": 12,
        "description": "Column expression without alias. Use explicit `AS` clause.",
        "name": "aliasing.expression",
        "fixes": [],
        "warning": False,
        "source_position": (11, 12),
    },
    {
        "code": "CP01",
        "line_no": 1,
        "line_pos": 20,
        "description": "Keywords must be consistently upper case.",
        "name": "capitalisation.keywords",
        "fixes": [{"type": "replace", "edit": "AS", "source_position": (19, 21)}],
        "warning": False,
        "source_position": (19, 21),
    },
    {
        "code": "LT01",
        "description": (
            "Expected only single space before naked identifier. Found '  '."
        ),
        "line_no": 1,
        "line_pos": 22,
        "name": "layout.spacing",
        "fixes": [{"type": "replace", "edit": " ", "source_position": (21, 23)}],
        "warning": False,
        "source_position": (21, 23),
    },
    {
        "code": "CP02",
        "line_no": 1,
        "line_pos": 24,
        "description": "Unquoted identifiers must be consistently lower case.",
        "name": "capitalisation.identifiers",
        "fixes": [{"type": "replace", "edit": "foo", "source_position": (23, 26)}],
        "warning": False,
        "source_position": (23, 26),
    },
    {
        "code": "LT01",
        "description": "Expected only single space before 'from' keyword. Found '  '.",
        "line_no": 1,
        "line_pos": 27,
        "name": "layout.spacing",
        "fixes": [{"type": "replace", "edit": " ", "source_position": (26, 28)}],
        "warning": False,
        "source_position": (26, 28),
    },
    {
        "code": "CP01",
        "line_no": 1,
        "line_pos": 29,
        "description": "Keywords must be consistently upper case.",
        "name": "capitalisation.keywords",
        "fixes": [{"type": "replace", "edit": "FROM", "source_position": (28, 32)}],
        "warning": False,
        "source_position": (28, 32),
    },
    {
        "code": "CP02",
        "line_no": 1,
        "line_pos": 34,
        "description": "Unquoted identifiers must be consistently lower case.",
        "name": "capitalisation.identifiers",
        "fixes": [{"type": "replace", "edit": "mytable", "source_position": (33, 40)}],
        "warning": False,
        "source_position": (33, 40),
    },
    {
        "code": "LT12",
        "line_no": 1,
        "line_pos": 41,
        "description": "Files must end with a single trailing newline.",
        "name": "layout.end_of_file",
        "fixes": [{"type": "create_after", "edit": "\n", "source_position": (0, 40)}],
        "warning": False,
        "source_position": (40, 40),
    },
]


def test__api__lint_string_without_violations():
    """Check lint functionality when there is no violation."""
    result = sqlfluff.lint("select column from table\n")
    assert result == []


def test__api__lint_string():
    """Basic checking of lint functionality."""
    result = sqlfluff.lint(my_bad_query)
    # Check return types.
    assert isinstance(result, list)
    assert all(isinstance(elem, dict) for elem in result)
    # Check actual result
    assert result == lint_result


def test__api__lint_string_specific():
    """Basic checking of lint functionality."""
    rules = ["CP02", "LT12"]
    result = sqlfluff.lint(my_bad_query, rules=rules)
    # Check which rules are found
    assert all(elem["code"] in rules for elem in result)


def test__api__lint_string_specific_single():
    """Basic checking of lint functionality."""
    rules = ["CP02"]
    result = sqlfluff.lint(my_bad_query, rules=rules)
    # Check which rules are found
    assert all(elem["code"] in rules for elem in result)


def test__api__lint_string_specific_exclude():
    """Basic checking of lint functionality."""
    exclude_rules = ["LT12", "CP01", "AL03", "CP02", "LT09", "LT01"]
    result = sqlfluff.lint(my_bad_query, exclude_rules=exclude_rules)
    # Check only AM04 is found
    assert len(result) == 1
    assert "AM04" == result[0]["code"]


def test__api__lint_string_specific_exclude_single():
    """Basic checking of lint functionality."""
    exclude_rules = ["LT01"]
    result = sqlfluff.lint(my_bad_query, exclude_rules=exclude_rules)
    # Check only AM04 is found
    assert len(result) == 9
    set(["LT12", "CP01", "AL03", "CP02", "LT09", "AM04"]) == set(
        [r["code"] for r in result]
    )


def test__api__lint_string_specific_exclude_all_failed_rules():
    """Basic checking of lint functionality."""
    exclude_rules = ["LT12", "CP01", "AL03", "CP02", "LT09", "LT01", "AM04"]
    result = sqlfluff.lint(my_bad_query, exclude_rules=exclude_rules)
    # Check it passes
    assert result == []


def test__api__fix_string():
    """Basic checking of lint functionality."""
    result = sqlfluff.fix(my_bad_query)
    # Check return types.
    assert isinstance(result, str)
    # Check actual result
    assert (
        result
        == """SELECT
    *,
    1,
    blah AS foo
FROM mytable
"""
    )


def test__api__fix_string_specific():
    """Basic checking of lint functionality with a specific rule."""
    result = sqlfluff.fix(my_bad_query, rules=["CP01"])
    # Check actual result
    assert result == "SELECT  *, 1, blah AS  fOO  FROM myTable"


def test__api__fix_string_specific_exclude():
    """Basic checking of lint functionality with a specific rule exclusion."""
    result = sqlfluff.fix(my_bad_query, exclude_rules=["LT09"])
    # Check actual result
    assert result == "SELECT *, 1, blah AS foo FROM mytable\n"


def test__api__fix_string_unparsable():
    """Test behavior with parse errors."""
    bad_query = """SELECT my_col
FROM my_schema.my_table
where processdate ! 3"""
    result = sqlfluff.fix(bad_query, rules=["CP01"])
    # Check fix result: should be unchanged because of the parse error.
    assert result == bad_query


def test__api__fix_string_unparsable_fix_even_unparsable():
    """Test behavior with parse errors."""
    bad_query = """SELECT my_col
FROM my_schema.my_table
where processdate ! 3"""
    result = sqlfluff.fix(bad_query, rules=["CP01"], fix_even_unparsable=True)
    # Check fix result: should be fixed because we overrode fix_even_unparsable.
    assert (
        result
        == """SELECT my_col
FROM my_schema.my_table
WHERE processdate ! 3"""
    )


def test__api__parse_string():
    """Basic checking of parse functionality."""
    parsed = sqlfluff.parse(my_bad_query)

    # Check a JSON object is returned.
    assert isinstance(parsed, dict)

    # Load in expected result.
    with open("test/fixtures/api/parse_test/parse_test.json", "r") as f:
        expected_parsed = json.load(f)

    # Compare JSON from parse to expected result.
    assert parsed == expected_parsed


def test__api__parse_fail():
    """Basic failure mode of parse functionality."""
    try:
        sqlfluff.parse("Select (1 + 2 +++) FROM mytable as blah blah")
        pytest.fail("sqlfluff.parse should have raised an exception.")
    except Exception as err:
        # Check it's the right kind of exception
        assert isinstance(err, sqlfluff.api.APIParsingError)
        # Check there are two violations in there.
        assert len(err.violations) == 2
        # Check it prints nicely.
        assert (
            str(err)
            == """Found 2 issues while parsing string.
Line 1, Position 15: Found unparsable section: '+++'
Line 1, Position 41: Found unparsable section: 'blah'"""
        )


def test__api__config_path():
    """Test that we can load a specified config file in the Simple API."""
    # Load test SQL file.
    with open("test/fixtures/api/config_path_test/config_path_test.sql", "r") as f:
        sql = f.read()

    # Pass a config path to the Simple API.
    parsed = sqlfluff.parse(
        sql,
        config_path="test/fixtures/api/config_path_test/extra_configs/.sqlfluff",
    )

    # Load in expected result.
    with open("test/fixtures/api/config_path_test/config_path_test.json", "r") as f:
        expected_parsed = json.load(f)

    # Compare JSON from parse to expected result.
    assert parsed == expected_parsed


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        (
            # No override from API, so uses .sqlfluff value
            {},
            set(),
        ),
        (
            # API overrides, so it uses that
            dict(exclude_rules=["RF02"]),
            {"RF04"},
        ),
    ],
)
def test__api__config_override(kwargs, expected, tmpdir):
    """Test that parameters to lint() override .sqlfluff correctly (or not)."""
    config_path = "test/fixtures/api/config_override/.sqlfluff"
    sql = "SELECT TRIM(name) AS name FROM some_table"
    lint_results = sqlfluff.lint(sql, config_path=config_path, **kwargs)
    assert expected == {"RF02", "RF04"}.intersection(
        {lr["code"] for lr in lint_results}
    )


def test__api__invalid_dialect():
    """Test that SQLFluffUserError is raised for a bad dialect."""
    # Load test SQL file.
    with open("test/fixtures/api/config_path_test/config_path_test.sql", "r") as f:
        sql = f.read()

    # Pass a fake dialect to the API and test the correct error is raised.
    with pytest.raises(SQLFluffUserError) as err:
        sqlfluff.parse(
            sql,
            dialect="not_a_real_dialect",
            config_path="test/fixtures/api/config_path_test/extra_configs/.sqlfluff",
        )

    assert str(err.value) == "Error: Unknown dialect 'not_a_real_dialect'"
