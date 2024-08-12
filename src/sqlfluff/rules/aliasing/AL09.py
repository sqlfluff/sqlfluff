"""Implementation of rule AL09."""

from typing import List

from sqlfluff.core.rules import BaseRule, LintFix, LintResult
from sqlfluff.core.rules.base import EvalResultType
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, Segments, sp


class Rule_AL09(BaseRule):
    """Column alias should not alias to itself, i.e. self-alias.

    Renaming the column to itself is a redundant piece of SQL,
    which doesn't affect its functionality.

    .. note::
        Note that this rule allows self-alias to change case sensitivity.

        However, when the case is changed without using quotes, the rule is
        not ``sqlfluff fix`` compatible.

    **Anti-pattern**

    Aliasing the column to itself.

    .. code-block:: sql

        SELECT
            col AS col,
            anycase AS "AnYcAsE",        -- Original case of column should be mentioned
            casechange AS CaseChange     -- Original case of column should be mentioned,
                                         -- and alias should be quoted
        FROM table;

    **Best practice**

    Not to use alias to rename the column to its original name.
    Self-aliasing leads to redundant code without changing any functionality.

    .. code-block:: sql

        SELECT
            col,
            "ANYCASE" AS "AnYcAsE",         -- Not fix compatible
            "casechange" AS "CaseChange"    -- Not fix compatible
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
        dialect = context.dialect.name
        DIALECTS_WITH_STRICT_COLUMN_CASE = ["snowflake", "oracle"]

        children: Segments = FunctionalContext(context).segment.children()

        for clause_element in children.select(sp.is_type("select_clause_element")):

            column = clause_element.get_child("column_reference")  # `col_a`
            alias_expression = clause_element.get_child(
                "alias_expression"
            )  # `as col_a`

            # If the alias is for a column_reference type,
            # and not: function or literal, then continue
            if alias_expression and column:
                # If column has either a naked_identifier or quoted_identifier
                # (not positional identifier like $n in snowflake)
                # then continue
                if column.get_child("naked_identifier") or column.get_child(
                    "quoted_identifier"
                ):
                    whitespace = clause_element.get_child("whitespace")  # ` `

                    is_column_quoted = False
                    is_alias_quoted = False
                    column_identifier = None
                    alias_identifier = None

                    # If the column name is quoted then get the `quoted_identifier`,
                    # otherwise get the last `naked_identifier`.
                    # The last naked_identifier in column_reference type
                    # belongs to the column name.
                    # Example: a.col_name where `a` is table name/alias identifier
                    if column.get_child("quoted_identifier"):
                        column_identifier = column.get_child("quoted_identifier")
                        is_column_quoted = True
                    else:
                        column_identifier = column.get_children("naked_identifier")[-1]

                    # The alias can be the naked_identifier or the quoted_identifier
                    if alias_expression.get_child("quoted_identifier"):
                        alias_identifier = alias_expression.get_child(
                            "quoted_identifier"
                        )
                        is_alias_quoted = True
                    elif alias_expression.get_child("naked_identifier"):
                        alias_identifier = alias_expression.get_child(
                            "naked_identifier"
                        )

                    assert whitespace and column_identifier and alias_identifier

                    column_identifier_naked = column_identifier.raw.strip("\"'`")
                    alias_identifier_naked = alias_identifier.raw.strip("\"'`")

                    # Case of column and alias is same
                    if column_identifier_naked == alias_identifier_naked:

                        # Allow Case Sensitivity change for dialects with strict case
                        if dialect in DIALECTS_WITH_STRICT_COLUMN_CASE and (
                            is_column_quoted != is_alias_quoted
                        ):
                            continue

                        # For dialects that allow columns to be queried using
                        # any case, the initial case of the column should be
                        # reflected during case change.
                        if (
                            (not is_column_quoted)
                            and (is_alias_quoted)
                            and (dialect not in DIALECTS_WITH_STRICT_COLUMN_CASE)
                        ):
                            violations.append(
                                LintResult(
                                    anchor=clause_element,
                                    description="The original case of column should \
                                        be reflected when case is changed.",
                                )
                            )
                        else:
                            # Self Alias
                            fixes: List[LintFix] = []

                            fixes.append(LintFix.delete(whitespace))
                            fixes.append(LintFix.delete(alias_expression))

                            violations.append(
                                LintResult(
                                    anchor=clause_element,
                                    description="Column should not be self-aliased.",
                                    fixes=fixes,
                                )
                            )

                    # When case is changed, the alias should be quoted
                    # Example: column AS "CoLuMn"
                    elif (
                        column_identifier_naked.upper()
                        == alias_identifier_naked.upper()
                    ) and not is_alias_quoted:
                        violations.append(
                            LintResult(
                                anchor=clause_element,
                                description="The column and alias should be \
                                    quoted when case of column is changed.",
                            )
                        )

        return violations or None
