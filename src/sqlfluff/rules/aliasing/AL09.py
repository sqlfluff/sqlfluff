"""Implementation of rule AL09."""

from typing import List

from sqlfluff.core.rules import BaseRule, LintFix, LintResult
from sqlfluff.core.rules.base import EvalResultType
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.dialects import dialect_ansi
from sqlfluff.dialects.dialect_ansi import AliasExpressionSegment
from sqlfluff.utils.functional import FunctionalContext, Segments, sp


class Rule_AL09(BaseRule):
    """Column alias should not alias to itself, i.e. self-alias.

    Renaming the column to itself is a redundant piece of SQL,
    which doesn't affect its functionality.

    Note that this rule does allow self-alias to change case sensitivity.
    In this case, the alias should be quoted. This ensures capitalisation
    rules are adhered.

    **Anti-pattern**

    Aliasing the column to itself.

    .. code-block:: sql

        SELECT
            col AS col,
            casechange AS CaseChange
        FROM table;

    **Best practice**

    Not to use alias to rename the column to its original name.
    Self-aliasing leads to redundant code without changing any functionality.

    .. code-block:: sql

        SELECT
            col,
            casechange AS "CaseChange"
        FROM table;
    """

    name = "aliasing.self_alias.column"
    groups = ("all", "core", "aliasing")
    crawl_behaviour = SegmentSeekerCrawler({"select_clause"})
    is_fix_compatible = True
    dialect_column_quotes_dict = {"bigquery": "`"}

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
        quote_char = self.dialect_column_quotes_dict.get(context.dialect.name, '"')

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

                    if column_identifier.raw == alias_identifier.raw:

                        # Self Alias when raw of column and alias is same
                        # and both are either naked or quoted
                        if is_column_quoted == is_alias_quoted:
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
                        column_identifier.raw_upper == alias_identifier.raw_upper
                    ) and not is_alias_quoted:
                        violations.append(
                            self._get_case_change_lint_result(
                                quote_char,
                                clause_element,
                                alias_expression,
                                alias_identifier,
                            )
                        )

        return violations or None

    def _get_case_change_lint_result(
        self, quote_char, clause_element, alias_expression, alias_identifier
    ):
        fixes = []

        as_keyword = dialect_ansi.KeywordSegment("as")
        fixes.append(
            LintFix.replace(
                alias_expression,
                [
                    AliasExpressionSegment(
                        (
                            as_keyword,
                            dialect_ansi.WhitespaceSegment(),
                            dialect_ansi.IdentifierSegment(
                                quote_char + alias_identifier.raw + quote_char,
                                type="quoted_identifier",
                            ),
                        )
                    )
                ],
            )
        )
        return LintResult(
            anchor=clause_element,
            description="The alias should be quoted when case of column is changed.",
            fixes=fixes,
        )
