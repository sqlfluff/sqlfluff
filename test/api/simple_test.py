"""Tests for simple use cases of the public api.

These tests should also test the imports, not just the functionality.
"""


def test__api__lint_string():
    """Basic checking of lint functionality."""
    import sqlfluff

    my_bad_query = "SeLEct  *, 1, blah as  fOO  from myTable"
    result = sqlfluff.lint(my_bad_query)

    # Check return types.
    assert isinstance(result, list)
    assert all(isinstance(elem, dict) for elem in result)
    # Check actual result
    assert result == [
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
