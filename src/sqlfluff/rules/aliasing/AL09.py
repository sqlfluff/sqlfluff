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

        # The dialect supports case insensitive naming for a column name, (e.g. COL1
        # is the same as col1) but the value in the result set name is case sensitive.
        # We use this to replace the column reference with the alias instead of just
        # removing the alias.
        dialect_supports_ci_names_cs_result = ["tsql", "bigquery"]

        ci_names_cs_result = context.dialect.name in dialect_supports_ci_names_cs_result

        for clause_element in children.select(sp.is_type("select_clause_element")):
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
                if column.get_child("naked_identifier", "quoted_identifier"):
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
                        "naked_identifier", "quoted_identifier"
                    )

                    if not whitespace or not column_identifier or not alias_identifier:
                        continue

                    # Column self-aliased
                    if (
                        column_identifier.raw_normalized()
                        # We casefold the alias only if it relevant in the result set.
                        == alias_identifier.raw_normalized(ci_names_cs_result)
                    ):
                        fixes: List[LintFix] = []

                        if ci_names_cs_result:
                            fixes.append(
                                LintFix.replace(column_identifier, [alias_identifier])
                            )
                        fixes.append(LintFix.delete(whitespace))
                        fixes.append(LintFix.delete(alias_expression))

                        violations.append(
                            LintResult(
                                anchor=clause_element,
                                description="Column should not be self-aliased.",
                                fixes=fixes,
                            )
                        )

        return violations or None
