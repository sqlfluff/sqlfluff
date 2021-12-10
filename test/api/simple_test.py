"""Tests for simple use cases of the public api."""

import json

import pytest

import sqlfluff
from sqlfluff.core.errors import SQLFluffUserError

my_bad_query = "SeLEct  *, 1, blah as  fOO  from myTable"

lint_result = [
    {
        "code": "L010",
        "line_no": 1,
        "line_pos": 1,
        "description": "Keywords must be consistently upper case.",
    },
    {
        "code": "L036",
        "description": "Select targets should be on a new line unless there is only one select target.",
        "line_no": 1,
        "line_pos": 1,
    },
    {
        "code": "L044",
        "description": "Query produces an unknown number of result columns.",
        "line_no": 1,
        "line_pos": 1,
    },
    {
        "code": "L039",
        "description": "Unnecessary whitespace found.",
        "line_no": 1,
        "line_pos": 7,
    },
    {
        "code": "L013",
        "line_no": 1,
        "line_pos": 12,
        "description": "Column expression without alias. Use explicit `AS` clause.",
    },
    {
        "code": "L010",
        "line_no": 1,
        "line_pos": 20,
        "description": "Keywords must be consistently upper case.",
    },
    {
        "code": "L039",
        "description": "Unnecessary whitespace found.",
        "line_no": 1,
        "line_pos": 22,
    },
    {
        "code": "L014",
        "line_no": 1,
        "line_pos": 24,
        "description": "Unquoted identifiers must be consistently lower case.",
    },
    {
        "code": "L039",
        "description": "Unnecessary whitespace found.",
        "line_no": 1,
        "line_pos": 27,
    },
    {
        "code": "L010",
        "line_no": 1,
        "line_pos": 29,
        "description": "Keywords must be consistently upper case.",
    },
    {
        "code": "L009",
        "line_no": 1,
        "line_pos": 34,
        "description": "Files must end with a single trailing newline.",
    },
    {
        "code": "L014",
        "line_no": 1,
        "line_pos": 34,
        "description": "Unquoted identifiers must be consistently lower case.",
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
    rules = ["L014", "L009"]
    result = sqlfluff.lint(my_bad_query, rules=rules)
    # Check which rules are found
    assert all(elem["code"] in rules for elem in result)


def test__api__lint_string_specific_single():
    """Basic checking of lint functionality."""
    rules = ["L014"]
    result = sqlfluff.lint(my_bad_query, rules=rules)
    # Check which rules are found
    assert all(elem["code"] in rules for elem in result)


def test__api__lint_string_specific_exclude():
    """Basic checking of lint functionality."""
    exclude_rules = ["L009", "L010", "L013", "L014", "L036", "L039"]
    result = sqlfluff.lint(my_bad_query, exclude_rules=exclude_rules)
    # Check only L044 is found
    assert len(result) == 1
    assert "L044" == result[0]["code"]


def test__api__lint_string_specific_exclude_single():
    """Basic checking of lint functionality."""
    exclude_rules = ["L039"]
    result = sqlfluff.lint(my_bad_query, exclude_rules=exclude_rules)
    # Check only L044 is found
    assert len(result) == 9
    set(["L009", "L010", "L013", "L014", "L036", "L044"]) == set(
        [r["code"] for r in result]
    )


def test__api__lint_string_specific_exclude_all_failed_rules():
    """Basic checking of lint functionality."""
    exclude_rules = ["L009", "L010", "L013", "L014", "L036", "L039", "L044"]
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
    result = sqlfluff.fix(my_bad_query, rules=["L010"])
    # Check actual result
    assert result == "SELECT  *, 1, blah AS  fOO  FROM myTable"


def test__api__fix_string_specific_exclude():
    """Basic checking of lint functionality with a specific rule exclusion."""
    result = sqlfluff.fix(my_bad_query, exclude_rules=["L036"])
    # Check actual result
    assert result == "SELECT *, 1, blah AS foo FROM mytable\n"


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
Line 1, Position 14: Found unparsable section: ' +++'
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
