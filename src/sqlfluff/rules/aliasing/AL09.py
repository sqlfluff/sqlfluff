"""Implementation of rule AL09."""

from typing import List

from sqlfluff.core.rules import BaseRule, LintFix, LintResult
from sqlfluff.core.rules.base import EvalResultType
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, Segments, sp


class Rule_AL09(BaseRule):
    """Column aliases should not alias to itself, i.e. self-alias.

    Renaming the column to itself is a redundant piece of SQL,
    which doesn't affect its functionality.

    Note that this rule does allow self-alias to change case sensitivity.

    **Anti-pattern**

    Aliasing the column to itself.

    .. code-block:: sql

        SELECT
            col AS col
        FROM table;

    **Best practice**

    Not to use alias to rename the column to its original name.
    Self-aliasing leads to redundant code without changing any functionality.

    .. code-block:: sql

        SELECT
            col
        FROM table;
    """

    name = "aliasing.self_alias.column"
    groups = ("all", "core", "aliasing")
    crawl_behaviour = SegmentSeekerCrawler({"select_clause"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Find self-aliased columns and fix them.

        Checks the alias in the `SELECT` clause and see if the
        alias identifier is same as the column identifier (self-alias).

        If the column is self-aliased, then the `AS` keyword,
        whitespaces and alias identifier is removed as part of the fix.
        For example: `col_a as col_a,` is fixed to `col_a,`
        """
        assert context.segment.is_type("select_clause")

        violations = []

        children: Segments = FunctionalContext(context).segment.children()

        for clause_element in children.select(sp.is_type("select_clause_element")):
            clause_element_raw_segments = (
                clause_element.get_raw_segments()
            )  # col_a as col_a

            column = clause_element.get_child("column_reference")  # `col_a`
            alias_expression = clause_element.get_child(
                "alias_expression"
            )  # `as col_a`

            # If the alias is for a column_reference type (not function)
            # then continue
            if alias_expression and column:
                # If column has either a naked_identifier or quoted_identifier
                # (not positional identifier like $n in snowflake)
                # then continue
                if column.get_child("naked_identifier") or column.get_child(
                    "quoted_identifier"
                ):
                    whitespace = clause_element.get_child("whitespace")  # ` `

                    # If the column name is quoted then get the `quoted_identifier`,
                    # otherwise get the last `naked_identifier`.
                    # The last naked_identifier in column_reference type
                    # belongs to the column name.
                    # Example: a.col_name where `a` is table name/alias identifier
                    if column.get_child("quoted_identifier"):
                        column_identifier = column.get_child("quoted_identifier")
                    else:
                        column_identifier = column.get_children("naked_identifier")[-1]

                    # The alias can be the naked_identifier or the quoted_identifier
                    alias_identifier = alias_expression.get_child(
                        "naked_identifier"
                    ) or alias_expression.get_child("quoted_identifier")

                    assert whitespace and column_identifier and alias_identifier

                    # Column self-aliased
                    if column_identifier.raw_upper == alias_identifier.raw_upper:
                        fixes: List[LintFix] = []

                        fixes.append(LintFix.delete(whitespace))
                        fixes.append(LintFix.delete(alias_expression))

                        violations.append(
                            LintResult(
                                anchor=clause_element_raw_segments[0],
                                description="Column should not be self-aliased.",
                                fixes=fixes,
                            )
                        )

        return violations or None
