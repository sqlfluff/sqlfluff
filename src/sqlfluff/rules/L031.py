"""Implementation of Rule L031."""

from collections import Counter, defaultdict
from typing import Generator, NamedTuple, Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


class TableAliasInfo(NamedTuple):
    """Structure yielded by_filter_table_expressions()."""

    table_ref: BaseSegment
    whitespace_ref: BaseSegment
    alias_exp_ref: BaseSegment
    alias_identifier_ref: BaseSegment


@document_fix_compatible
class Rule_L031(BaseRule):
    """Avoid table aliases in from clauses and join conditions.

    | **Anti-pattern**
    | In this example, alias 'o' is used for the orders table, and 'c' is used for 'customers' table.

    .. code-block:: sql

        SELECT
            COUNT(o.customer_id) as order_amount,
            c.name
        FROM orders as o
        JOIN customers as c on o.id = c.user_id


    | **Best practice**
    |  Avoid aliases.

    .. code-block:: sql

        SELECT
            COUNT(orders.customer_id) as order_amount,
            customers.name
        FROM orders
        JOIN customers on orders.id = customers.user_id

        -- Self-join will not raise issue

        SELECT
            table.a,
            table_alias.b,
        FROM
            table
            LEFT JOIN table AS table_alias ON table.foreign_key = table_alias.foreign_key

    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Identify aliases in from clause and join conditions.

        Find base table, table expressions in join, and other expressions in select clause
        and decide if it's needed to report them.
        """
        if context.segment.is_type("select_statement"):
            # A buffer for all table expressions in join conditions
            from_expression_elements = []
            column_reference_segments = []

            from_clause_segment = context.segment.get_child("from_clause")

            if not from_clause_segment:
                return None

            from_expression = from_clause_segment.get_child("from_expression")
            from_expression_element = None
            if from_expression:
                from_expression_element = from_expression.get_child(
                    "from_expression_element"
                )

            if not from_expression_element:
                return None
            from_expression_element = from_expression_element.get_child(
                "table_expression"
            )

            # Find base table
            base_table = None
            if from_expression_element:
                base_table = from_expression_element.get_child("object_reference")

            from_clause_index = context.segment.segments.index(from_clause_segment)
            from_clause_and_after = context.segment.segments[from_clause_index:]

            for clause in from_clause_and_after:
                for from_expression_element in clause.recursive_crawl(
                    "from_expression_element"
                ):
                    from_expression_elements.append(from_expression_element)
                for column_reference in clause.recursive_crawl("column_reference"):
                    column_reference_segments.append(column_reference)

            return (
                self._lint_aliases_in_join(
                    base_table,
                    from_expression_elements,
                    column_reference_segments,
                    context.segment,
                )
                or None
            )
        return None

    @classmethod
    def _filter_table_expressions(
        cls, base_table, from_expression_elements
    ) -> Generator[TableAliasInfo, None, None]:
        for from_expression in from_expression_elements:
            table_expression = from_expression.get_child("table_expression")
            if not table_expression:
                continue
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
    ):
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
            alias_name = alias_info.alias_identifier_ref.raw
            for alias_with_column in select_clause.recursive_crawl("object_reference"):
                used_alias_ref = alias_with_column.get_child("identifier")
                if used_alias_ref and used_alias_ref.raw == alias_name:
                    ids_refs.append(used_alias_ref)

            # Find all references to alias in column references
            for exp_ref in column_reference_segments:
                used_alias_ref = exp_ref.get_child("identifier")
                # exp_ref.get_child('dot') ensures that the column reference includes a table reference
                if (
                    used_alias_ref
                    and used_alias_ref.raw == alias_name
                    and exp_ref.get_child("dot")
                ):
                    ids_refs.append(used_alias_ref)

            # Fixes for deleting ` as sth` and for editing references to aliased tables
            fixes = [
                *[
                    LintFix.delete(d)
                    for d in [alias_info.alias_exp_ref, alias_info.whitespace_ref]
                ],
                *[
                    LintFix.replace(alias, [alias.edit(alias_info.table_ref.raw)])
                    for alias in [alias_info.alias_identifier_ref, *ids_refs]
                ],
            ]

            violation_buff.append(
                LintResult(
                    anchor=alias_info.alias_identifier_ref,
                    description="Avoid aliases in from clauses and join conditions.",
                    fixes=fixes,
                )
            )

        return violation_buff or None
