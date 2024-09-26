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
    which doesn't affect its functionality. This rule only applies
    when the current dialect would resolve the two identifiers to
    the same object. Aliases which effectively change the casing of
    an identifier as still allowed.

    In all dialects, aliasing to an exact copy of the column reference
    is always unnecessary (e.g. :code:`foo as foo` or :code:`"BAR" as "BAR"`).
    The situation which is dialect dependent is how the alias is treated
    when the quoting and casing of the two are not the same. We allow
    users to override this behaviour using the :code:`self_alias_casing`
    config value, but the default behaviour is to attempt to auto detect from
    the dialect (i.e. with :code:`self_alias_casefold` set to :code:`dialect`).

    .. list-table::
       :widths: 26 48 26
       :header-rows: 1

       * - :code:`self_alias_casing` setting / Dialect behaviour
         - ⚠️ Self-alias examples.
         - ✅ Re-casing examples.
       * - :code:`unquoted_sensitive`. Default for :ref:`clickhouse_dialect_ref`,
           :ref:`trino_dialect_ref` and :ref:`bigquery_dialect_ref`, and known
           to be an optional configuration for :ref:`tsql_dialect_ref` instances.
           See :ref:`note <note_about_bigquery_and_clickhouse>` below.
         - This is the most conservative setting, which restricts this rule
           to only flag self aliases, when the casing is exactly the same,
           even when unquoted e.g. :code:`"Foo" as "Foo"`.
         - Any case change (even un-quoted) is a re-casing alias e.g.
           :code:`Foo as fOo` or :code:`"Foo" as "foo"`.
       * - :code:`quoted_insensitive` & case insensitive dialects e.g.
           :ref:`duckdb_dialect_ref` or :ref:`sparksql_dialect_ref`
         - Regardless of quotes or casing, all aliases which compare the same
           as their references are self-aliases e.g. :code:`"Foo" as fOo`.
         - NA. Re-casing is not possible in these dialects. The case of the
           object as it was originally defined is always returned.
       * - :code:`unquoted_uppercase` natively :code:`UPPERCASE` dialects
           e.g. :ref:`snowflake_dialect_ref`, :ref:`tsql_dialect_ref` &
           :ref:`oracle_dialect_ref` i.e. dialects where unquoted
           identifiers are treated as uppercase.
         - Identifiers which all resolve to the default casing of :code:`FOO`
           e.g. :code:`foo as foo`, :code:`foo as FOO`, :code:`Foo as "FOO"`
           & :code:`"FOO" as FOO`.
         - Aliases which resolve to a different case e.g.
           :code:`"foo" as foo`, :code:`"Foo" as "FOO"`
       * - :code:`unquoted_lowercase` & natively :code:`lowercase` dialects
           e.g. :ref:`athena_dialect_ref`, :ref:`hive_dialect_ref`,
           :ref:`postgres_dialect_ref` & :ref:`mysql_dialect_ref` i.e. dialects
           where unquoted identifiers are treated as lowercase.
         - Identifiers which all resolve to the default casing of :code:`foo`
           e.g. :code:`foo as foo`, :code:`foo as FOO`, :code:`Foo as "foo"`
           & :code:`"foo" as foo`.
         - Aliases which resolve to a different case e.g.
           :code:`"FOO" as FOO`, :code:`"Foo" as "foo"`

    This rule is closely associated with (and constrained by the same above
    factors) as :sqlfluff:ref:`references.quoting` (:sqlfluff:ref:`RF06`).

    .. _note_about_bigquery_and_clickhouse:

    .. note::

       While :ref:`clickhouse_dialect_ref` and :ref:`bigquery_dialect_ref`
       default to the same setting for this rule, they do that for different
       reasons.

       :ref:`clickhouse_dialect_ref` is case sensitive throughout, regardless
       of whether identifiers or aliases are quoted or unquoted. If a column
       is defined as :code:`foo` and then a user runs :code:`select FOO from my_table`
       then Clickhouse will return a :code:`UNKNOWN_IDENTIFIER` error.

       :ref:`bigquery_dialect_ref` and :ref:`trino_dialect_ref` store column
       casing differently, but both of them *resolve* references case insensitively.
       However both of them also respect the case of references in the result set
       without aliasing. As a result, re-casing can be done without quoting.

       It's worth noting that for these dialects, you may wish to disable
       :sqlfluff:ref:`capitalisation.identifiers` (:sqlfluff:ref:`CP02`) for the
       project as that will otherwise coerce any unquoted identifiers to the default
       capitalisation. This may be undesirable if you wish to take advantage of
       this casing behaviour in any of these dialects.

       As a general rule, the case sensitivity of different dialects varies
       significantly, and as such we recommend using a single consistent approach
       to casing across your project if at all possible.

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
            COL,
            -- Re-casing aliasing is still allowed where necessary
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

                    if not (
                        whitespace and column_identifier and alias_identifier
                    ):  # pragma: no cover
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
                            f"column_identifier: {column_identifier is not None}, "
                            f"alias_identifier: {alias_identifier is not None}, "
                            f"alias_expression: {clause_element.raw!r}."
                        )
                        continue

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
