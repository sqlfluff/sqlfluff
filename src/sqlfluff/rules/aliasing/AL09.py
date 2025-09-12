"""Implementation of rule AL09."""

from sqlfluff.core.rules import BaseRule, LintFix, LintResult
from sqlfluff.core.rules.base import EvalResultType
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, Segments, sp


class Rule_AL09(BaseRule):
    """Column aliases should not alias to itself, i.e. self-alias.

    Renaming the column to itself is a redundant piece of SQL,
    which doesn't affect its functionality. This rule only applies
    when aliasing to an exact copy of the column reference (e.g.
    :code:`foo as foo` or :code:`"BAR" as "BAR"`, see note below on
    more complex examples). Aliases which effectively change the casing of
    an identifier are still allowed.

    .. note::

       This rule works in conjunction with :sqlfluff:ref:`references.quoting`
       (:sqlfluff:ref:`RF06`) and :sqlfluff:ref:`capitalisation.identifiers`
       (:sqlfluff:ref:`CP02`) to handle self aliases with mixed quoting
       and casing. In the situation that these two rules are not enabled
       then this rule will only fix the strict case where the quoting
       and casing of the alias and reference are the same.

       If those two rules are enabled, the fixes applied may result in a
       situation where this rule can kick in as a secondary effect. For
       example this :ref:`snowflake_dialect_ref` query:

       .. code-block:: sql

          -- Original Query. AL09 will not trigger because casing and
          -- quoting are different. RF06 will however fix the unnecessary
          -- quoting of "COL".
          SELECT "COL" AS col FROM table;
          -- After RF06, the query will look like this, at which point
          -- CP02 will see the inconsistent capitalisation. Depending
          -- on the configuration it will change one of the identifiers.
          -- Let's assume the default configuration of "consistent".
          SELECT COL AS col FROM table;
          -- After CP02, the alias and the reference will be the same
          -- and at this point AL09 can take over and remove the alias.
          SELECT COL AS COL FROM table;
          -- ..resulting in:
          SELECT COL FROM table;

       This interdependence between the rules, and the configuration
       options offered by each one means a variety of outcomes can be
       achieved by enabling and disabling each one. See
       :ref:`ruleselection` and :ref:`ruleconfig` for more details.

    **Anti-pattern**

    Aliasing the column to itself, where not necessary for changing the case
    of an identifier.

    .. code-block:: sql

        SELECT
            col AS col,
            "Col" AS "Col",
            COL AS col
        FROM table;

    **Best practice**

    Not to use alias to rename the column to its original name.
    Self-aliasing leads to redundant code without changing any functionality,
    unless used to effectively change the case of the identifier.

    .. code-block:: sql

        SELECT
            col,
            "Col"
            COL,
        FROM table;

        -- Re-casing aliasing is still allowed where necessary, i.e.
        SELECT
            col as "Col",
            "col" as "COL"
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

            # We're only interested in direct aliasing of columns (i.e. not
            # and expression), so if that isn't the case, move on.
            if not (alias_expression and column):
                continue

            # The column needs to be a naked_identifier or quoted_identifier
            # (not positional identifier like $n in snowflake).
            # Move on if not. Some column references have multiple elements
            # (e.g. my_table.my_column), so only fetch the last available.
            _column_elements = column.get_children(
                "naked_identifier", "quoted_identifier"
            )
            if not _column_elements:  # pragma: no cover
                continue
            column_identifier = _column_elements[-1]

            # Fetch the whitespace between the reference and the alias.
            whitespace = clause_element.get_child("whitespace")  # ` `

            # The alias can be the naked_identifier or the quoted_identifier
            alias_identifier = alias_expression.get_child(
                "naked_identifier", "quoted_identifier"
            )

            # if we do not have an alias identifier we can continue
            if not alias_identifier:  # pragma: no cover
                continue

            alias_keyword_raw = getattr(
                alias_expression.get_child("alias_operator"), "raw", None
            )
            # If the alias keyword is '=', then no whitespace have to be present
            # between the alias_keyword and the alias_identifier
            if alias_keyword_raw != "=":
                if not (whitespace and alias_identifier):  # pragma: no cover
                    # We *should* expect all of these to be non-null, but some bug
                    # reports suggest that that isn't always the case for some
                    # dialects. In those cases, log a warning here, but don't
                    # flag it as a linting issue. Hopefully this will help
                    # better bug reports in future.
                    self.logger.warning(
                        "AL09 found an unexpected syntax in an alias expression. "
                        "Unable to determine if this is a self-alias. Please "
                        "report this as a bug on GitHub.\n\n"
                        f"Debug details: dialect: {context.dialect.name}, "
                        f"whitespace: {whitespace is not None}, "
                        f"alias_identifier: {alias_identifier is not None}, "
                        f"alias_expression: {clause_element.raw!r}."
                    )
                    continue

            case_sensitive_dialects = ["clickhouse"]

            # We compare the _exact_ raw value of the column identifier
            # and the alias identifier (i.e. including quoting and casing).
            # Resolving aliases & references with differing quoting and casing
            # should be done in conjunction with RF06 & CP02 (see docstring).
            if column_identifier.raw == alias_identifier.raw:
                fixes: list[LintFix] = []

                if whitespace is not None:
                    fixes.append(LintFix.delete(whitespace))
                fixes.append(LintFix.delete(alias_expression))

                violations.append(
                    LintResult(
                        anchor=clause_element_raw_segments[0],
                        description="Column should not be self-aliased.",
                        fixes=fixes,
                    )
                )
            # If *both* are unquoted, and we're in a dialect which isn't case
            # sensitive for unquoted identifiers, then flag an error but don't
            # suggest a fix. It's ambiguous about what the users intent was:
            # i.e. did they mean to change the case (and so the correct
            # resolution is quoting), or did they mistakenly add an unnecessary
            # alias?
            elif (
                context.dialect.name not in case_sensitive_dialects
                and column_identifier.is_type("naked_identifier")
                and alias_identifier is not None
                and alias_identifier.is_type("naked_identifier")
                and column_identifier.raw_upper == alias_identifier.raw_upper
            ):
                violations.append(
                    LintResult(
                        anchor=clause_element_raw_segments[0],
                        description=(
                            "Ambiguous self alias. Either remove unnecessary "
                            "alias, or quote alias/reference to make case "
                            "change explicit."
                        ),
                    )
                )

        return violations or None
