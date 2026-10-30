"""Tests the python routines within AL04."""

import sqlfluff
from sqlfluff.core import Linter
from sqlfluff.core.rules import LintResult
from sqlfluff.rules.aliasing.AL04 import Rule_AL04


class Rule_T004(Rule_AL04):
    """A rule based on AL04, which reports everything its method is given."""

    groups = ("all",)
    name = "test.aliases_subclass"
    aliases = ()

    def _lint_references_and_aliases(
        self,
        table_aliases,
        standalone_aliases,
        references,
        col_aliases,
        using_cols,
        parent_select,
        rule_context,
    ):
        results = [
            LintResult(anchor=r, description=f"reference {r.raw}") for r in references
        ]
        results += [
            LintResult(
                anchor=c.aliased_segment,
                description=f"column alias {c.alias_identifier_name}",
            )
            for c in col_aliases
        ]
        results += [
            LintResult(anchor=u, description=f"using column {u.raw}")
            for u in using_cols
        ]
        return results or None


def test__rules__std_AL04_subclass_method_is_given_references():
    """A subclass which overrides the method is given more than the aliases.

    AL04 itself only reads the table and standalone aliases of each SELECT, but
    subclasses override `_lint_references_and_aliases()` and may also read the
    references, column aliases and USING columns.
    """
    sql = "SELECT a, t.b AS c\nFROM tbl AS t\nJOIN u USING (id)\nWHERE t.x = 1\n"
    linter = Linter(user_rules=[Rule_T004], dialect="ansi", rules=["T004"])
    result = linter.lint_string(sql)
    assert sorted(v.desc() for v in result.get_violations()) == [
        "column alias c",
        "reference a",
        "reference t.b",
        "reference t.x",
        "using column id",
    ]


def test__rules__std_AL04_one_aliases_one_duplicate():
    """Verify correct error message for one duplicate table aliases occur one times."""
    sql = """
        SELECT
            a.pk
        FROM table_1 AS a
        JOIN table_2 AS a ON a.pk = a.pk
    """
    result = sqlfluff.lint(sql)
    assert "AL04" in [r["code"] for r in result]
    assert [r["code"] for r in result].count("AL04") == 1


def test__rules__std_AL04_one_aliases_two_duplicate():
    """Verify correct error message for one duplicate table aliases occur two times."""
    sql = """
        SELECT
            a.pk
        FROM table_1 AS a
        JOIN table_2 AS a ON a.pk = a.pk
        JOIN table_3 AS a ON a.pk = a.pk
    """
    result = sqlfluff.lint(sql)
    result_filter = [r for r in result if r["code"] == "AL04"]
    # Error message only show two times, not three
    assert len(result_filter) == 2
    assert (
        len(
            [
                r
                for r in result_filter
                if "Duplicate table alias 'a'" in r["description"]
            ]
        )
        == 2
    )
    # Test specific line number
    assert result_filter[0]["start_line_no"] == 5
    assert result_filter[1]["start_line_no"] == 6


def test__rules__std_AL04_complex():
    """Verify that AL04 returns the correct error message for complex example."""
    sql = """
        SELECT
            a.pk,
            b.pk
        FROM table_1 AS a
        JOIN table_2 AS a ON a.pk = a.pk
        JOIN table_3 AS b ON a.pk = b.pk
        JOIN table_4 AS b ON b.pk = b.pk
        JOIN table_5 AS a ON b.pk = a.pk
    """
    result = sqlfluff.lint(sql)
    result_filter = [r for r in result if r["code"] == "AL04"]
    # Error message only show two times, not three
    assert len(result_filter) == 3
    assert (
        len(
            [
                r
                for r in result_filter
                if "Duplicate table alias 'a'" in r["description"]
            ]
        )
        == 2
    )
    assert (
        len(
            [
                r
                for r in result_filter
                if "Duplicate table alias 'b'" in r["description"]
            ]
        )
        == 1
    )
    # Test specific line number
    assert result_filter[0]["start_line_no"] == 6
    assert result_filter[1]["start_line_no"] == 8
    assert result_filter[2]["start_line_no"] == 9
