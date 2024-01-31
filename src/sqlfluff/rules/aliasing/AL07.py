"""Implementation of Rule AL07."""

from collections import Counter, defaultdict
from typing import Generator, List, NamedTuple, Optional

from sqlfluff.core.parser import BaseSegment, IdentifierSegment, SymbolSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class TableAliasInfo(NamedTuple):
    """Structure yielded by_filter_table_expressions()."""

    table_ref: BaseSegment
    whitespace_ref: BaseSegment
    alias_exp_ref: BaseSegment
    alias_identifier_ref: BaseSegment


class Rule_AL07(BaseRule):
    """Avoid table aliases in from clauses and join conditions.

    .. note::
       This rule was taken from the `dbt Style Guide
       <https://github.com/dbt-labs/corp/blob/main/dbt_style_guide.md>`_
       which notes that:

        Avoid table aliases in join conditions (especially initialisms) - it's
        harder to understand what the table called "c" is compared to "customers".

       This rule is controversial and for many larger databases avoiding alias is
       neither realistic nor desirable. In particular for BigQuery due to the
       complexity of backtick requirements and determining whether a name refers
       to a project or dataset so automated fixes can potentially break working
       SQL code. For most users :class:`Rule_AL06` is likely a more appropriate
       linting rule to drive a sensible behaviour around aliasing.

       The stricter treatment of aliases in this rule may be useful for more
       focused projects, or temporarily as a refactoring tool because the
       :code:`fix` routine of the rule can remove aliases.

       This rule is disabled by default for all dialects it can be enabled with
       the ``force_enable = True`` flag.

    **Anti-pattern**

    In this example, alias ``o`` is used for the orders table, and ``c`` is used for
    ``customers`` table.

    .. code-block:: sql

        SELECT
            COUNT(o.customer_id) as order_amount,
            c.name
        FROM orders as o
        JOIN customers as c on o.id = c.user_id


    **Best practice**

    Avoid aliases.

    .. code-block:: sql

        SELECT
            COUNT(orders.customer_id) as order_amount,
            customers.name
        FROM orders
        JOIN customers on orders.id = customers.user_id

        -- Self-join will not raise issue

        SELECT
            table1.a,
            table_alias.b,
        FROM
            table1
            LEFT JOIN table1 AS table_alias ON
                table1.foreign_key = table_alias.foreign_key

    """

    name = "aliasing.forbid"
    aliases = ("L031",)
    groups = ("all", "aliasing")
    config_keywords = ["force_enable"]
    crawl_behaviour = SegmentSeekerCrawler({"select_statement"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Identify aliases in from clause and join conditions.

        Find base table, table expressions in join, and other expressions in select
        clause and decide if it's needed to report them.
        """
        # Config type hints
        self.force_enable: bool

        # Issue 2810: BigQuery has some tricky expectations (apparently not
        # documented, but subject to change, e.g.:
        # https://www.reddit.com/r/bigquery/comments/fgk31y/new_in_bigquery_no_more_backticks_around_table/)
        # about whether backticks are required (and whether the query is valid
        # or not, even with them), depending on whether the GCP project name is
        # present, or just the dataset name. Since SQLFluff doesn't have access
        # to BigQuery when it is looking at the query, it would be complex for
        # this rule to do the right thing. For now, the rule simply disables
        # itself.
        if not self.force_enable:
            return None

        assert context.segment.is_type("select_statement")

        children = FunctionalContext(context).segment.children()
        from_clause_segment = children.select(sp.is_type("from_clause")).first()
        base_table = (
            from_clause_segment.children(sp.is_type("from_expression"))
            .first()
            .children(sp.is_type("from_expression_element"))
            .first()
            .children(sp.is_type("table_expression"))
            .first()
            .children(sp.is_type("object_reference"))
            .first()
        )
        if not base_table:
            return None

        # A buffer for all table expressions in join conditions
        from_expression_elements = []
        column_reference_segments = []

        after_from_clause = children.select(start_seg=from_clause_segment[0])
        for clause in from_clause_segment + after_from_clause:
            for from_expression_element in clause.recursive_crawl(
                "from_expression_element"
            ):
                from_expression_elements.append(from_expression_element)
            for column_reference in clause.recursive_crawl("column_reference"):
                column_reference_segments.append(column_reference)

        return (
            self._lint_aliases_in_join(
                base_table[0] if base_table else None,
                from_expression_elements,
                column_reference_segments,
                context.segment,
            )
            or None
        )

    @classmethod
    def _filter_table_expressions(
        cls, base_table, from_expression_elements
    ) -> Generator[TableAliasInfo, None, None]:
        for from_expression in from_expression_elements:
            table_expression = from_expression.get_child("table_expression")
            if not table_expression:
                continue  # pragma: no cover
            table_ref = table_expression.get_child("object_reference")

            # If the from_expression_element has no object_references - skip it
            # An example case is a lateral flatten, where we have a function segment
            # instead of a table_reference segment.
            if not table_ref:
                continue

            # If this is self-join - skip it
            if (
                base_table
                and base_table.raw == table_ref.raw
                and base_table != table_ref
            ):
                continue

            whitespace_ref = from_expression.get_child("whitespace")

            # If there's no alias expression - skip it
            alias_exp_ref = from_expression.get_child("alias_expression")
            if alias_exp_ref is None:
                continue

            alias_identifier_ref = alias_exp_ref.get_child("identifier")
            yield TableAliasInfo(
                table_ref, whitespace_ref, alias_exp_ref, alias_identifier_ref
            )

    def _lint_aliases_in_join(
        self, base_table, from_expression_elements, column_reference_segments, segment
    ) -> Optional[List[LintResult]]:
        """Lint and fix all aliases in joins - except for self-joins."""
        # A buffer to keep any violations.
        violation_buff = []

        to_check = list(
            self._filter_table_expressions(base_table, from_expression_elements)
        )

        # How many times does each table appear in the FROM clause?
        table_counts = Counter(ai.table_ref.raw for ai in to_check)

        # What is the set of aliases used for each table? (We are mainly
        # interested in the NUMBER of different aliases used.)
        table_aliases = defaultdict(set)
        for ai in to_check:
            if ai and ai.table_ref and ai.alias_identifier_ref:
                table_aliases[ai.table_ref.raw].add(ai.alias_identifier_ref.raw)

        # For each aliased table, check whether to keep or remove it.
        for alias_info in to_check:
            # If the same table appears more than once in the FROM clause with
            # different alias names, do not consider removing its aliases.
            # The aliases may have been introduced simply to make each
            # occurrence of the table independent within the query.
            if (
                table_counts[alias_info.table_ref.raw] > 1
                and len(table_aliases[alias_info.table_ref.raw]) > 1
            ):
                continue

            select_clause = segment.get_child("select_clause")

            ids_refs = []

            # Find all references to alias in select clause
            if alias_info.alias_identifier_ref:
                alias_name = alias_info.alias_identifier_ref.raw
                for alias_with_column in select_clause.recursive_crawl(
                    "object_reference"
                ):
                    used_alias_ref = alias_with_column.get_child("identifier")
                    if used_alias_ref and used_alias_ref.raw == alias_name:
                        ids_refs.append(used_alias_ref)

            # Find all references to alias in column references
            for exp_ref in column_reference_segments:
                used_alias_ref = exp_ref.get_child("identifier")
                # exp_ref.get_child('dot') ensures that the column reference includes a
                # table reference
                if (
                    used_alias_ref
                    and used_alias_ref.raw == alias_name
                    and exp_ref.get_child("dot")
                ):
                    ids_refs.append(used_alias_ref)

            # Fixes for deleting ` as sth` and for editing references to aliased tables
            # Note unparsable errors have cause the delete to fail (see #2484)
            # so check there is a d before doing deletes.
            fixes: List[LintFix] = []
            fixes += [
                LintFix.delete(d)
                for d in [alias_info.alias_exp_ref, alias_info.whitespace_ref]
                if d
            ]
            for alias in [alias_info.alias_identifier_ref, *ids_refs]:
                if alias:
                    identifier_parts = alias_info.table_ref.raw.split(".")
                    edits: List[BaseSegment] = []
                    for part in identifier_parts:
                        if edits:
                            edits.append(SymbolSegment(".", type="dot"))
                        edits.append(IdentifierSegment(part, type="naked_identifier"))

                    fixes.append(
                        LintFix.replace(
                            alias,
                            edits,
                            source=[alias_info.table_ref],
                        )
                    )

            violation_buff.append(
                LintResult(
                    anchor=alias_info.alias_identifier_ref,
                    description="Avoid aliases in from clauses and join conditions.",
                    fixes=fixes,
                )
            )

        return violation_buff or None
