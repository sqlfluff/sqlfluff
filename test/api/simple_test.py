"""Tests for simple use cases of the public api.

These tests should also test the imports, not just the functionality.
"""

import io

import sqlfluff

my_bad_query = "SeLEct  *, 1, blah as  fOO  from myTable"

lint_result = [
    {
        "code": "L010",
        "line_no": 1,
        "line_pos": 1,
        "description": "Inconsistent capitalisation of keywords.",
    },
    {
        "code": "L013",
        "line_no": 1,
        "line_pos": 12,
        "description": "Column expression without alias. Use explicit `AS` clause.",
    },
    {
        "code": "L014",
        "line_no": 1,
        "line_pos": 24,
        "description": "Inconsistent capitalisation of unquoted identifiers.",
    },
    {
        "code": "L009",
        "line_no": 1,
        "line_pos": 34,
        "description": "Files must end with a trailing newline.",
    },
    {
        "code": "L014",
        "line_no": 1,
        "line_pos": 34,
        "description": "Inconsistent capitalisation of unquoted identifiers.",
    },
]


def test__api__lint_string():
    """Basic checking of lint functionality."""
    result = sqlfluff.lint(my_bad_query)
    # Check return types.
    assert isinstance(result, list)
    assert all(isinstance(elem, dict) for elem in result)
    # Check actual result
    assert result == lint_result


def test__api__lint_file():
    """Basic checking of lint functionality from a file object."""
    string_buffer = io.StringIO(my_bad_query)
    result = sqlfluff.lint(string_buffer)
    # Check actual result
    assert result == lint_result


def test__api__lint_string_specific():
    """Basic checking of lint functionality."""
    rules = ["L014", "L009"]
    result = sqlfluff.lint(my_bad_query, rules=rules)
    # Check which rules are found
    assert all(elem["code"] in rules for elem in result)


def test__api__fix_string():
    """Basic checking of lint functionality."""
    result = sqlfluff.fix(my_bad_query)
    # Check return types.
    assert isinstance(result, str)
    # Check actual result
    assert result == "SELECT  *, 1, blah AS  foo  FROM mytable\n"


def test__api__fix_string_specific():
    """Basic checking of lint functionality with a specific rule."""
    result = sqlfluff.fix(my_bad_query, rules="L010")
    # Check actual result
    assert result == "SELECT  *, 1, blah AS  fOO  FROM myTable"


def test__api__parse_string():
    """Basic checking of parse functionality."""
    parsed = sqlfluff.parse(my_bad_query)
    # Check we can call `to_tuple` on the result
    assert isinstance(parsed.to_tuple(), tuple)
    # Check we can iterate objects within it
    keywords = [keyword.raw for keyword in parsed.recursive_crawl("keyword")]
    assert keywords == ["SeLEct", "as", "from"]
    # Check we can get columns from it
    col_refs = [col_ref.raw for col_ref in parsed.recursive_crawl("column_reference")]
    assert col_refs == ["blah"]
    # Check we can get table from it
    tbl_refs = [tbl_ref.raw for tbl_ref in parsed.recursive_crawl("table_reference")]
    assert tbl_refs == ["myTable"]
