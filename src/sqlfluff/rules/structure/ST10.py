"""Implementation of Rule ST10."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext


class Rule_ST10(BaseRule):
    """Unused tables in joins should be removed.

    This rule will check if there are any tables that are referenced in the
    ``FROM`` or ``JOIN`` clause of a ``SELECT`` statement, but where no
    columns from that table are referenced in the any of the other clauses.

    This rule relies on all of the column references in the ``SELECT``
    statement being qualified with at least the table name, and so is
    designed to work alongside :sqlfluff:ref:`references.qualification`
    (:sqlfluff:ref:`RF02`).

    This rule does not propose a fix, because it assumes that it an unused
    table is a mistake, but doesn't know whether the mistake was the join,
    or the mistake was not using it.

    **Anti-pattern**

    In this example, the table ``bar`` is included in the ``JOIN`` clause
    but not columns from it are referenced in

    .. code-block:: sql

        SELECT
            foo.a,
            foo.b
        FROM foo
        LEFT JOIN bar ON foo.a = bar.a

    **Best practice**

    Remove the join, or use the table.

    .. code-block:: sql

        SELECT foo.a, vee.b
        FROM foo;

        SELECT
            foo.a,
            foo.b,
            bar.c
        FROM foo
        LEFT JOIN bar ON foo.a = bar.a

    In the (*very rare*) situations that it is logically necessary to include
    a table in a join clause, but not otherwise refer to it (likely for
    granularity reasons), we recommend ignoring this rule for that specific
    line by using ``-- noqa: ST10`` at the end of the line.
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Implement the logic to detect unused tables in joins.

        1. Get all the tables that are joined in the query.
        2. Get all the tables that are used in the select statement.
        3. Compare the two lists and find the tables that are in the join list but not in the select list.
        4. For each unused table, create a LintResult with a fix that removes the join.
        """
        join_tables = context.segment.get_children("join_clause")
        select_tables = context.segment.get_children("select_clause")
        unused_tables = [table for table in join_tables if table not in select_tables]
        for table in unused_tables:
            return LintResult(anchor=table, fixes=[LintFix("delete", table)])
        return None
