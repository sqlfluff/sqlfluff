"""Implementation of Rule L031."""

from sqlfluff.core.rules.base import BaseCrawler, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L031(BaseCrawler):
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

    def _eval(self, segment, **kwargs):
        """Identify aliases in from clause and join conditions.

        Find base table, table expressions in join, and other expressions in select clause
        and decide if it's needed to report them.
        """
        if segment.is_type("select_statement"):
            # A buffer for all table expressions in join conditions
            table_expression_segments = []
            column_reference_segments = []

            from_clause_segment = segment.get_child("from_clause")

            if not from_clause_segment:
                return None

            table_expression = from_clause_segment.get_child("table_expression")
            if not table_expression:
                return None
            table_expression = table_expression.get_child("main_table_expression")

            # Find base table
            base_table = None
            if table_expression:
                base_table = table_expression.get_child("object_reference")

            from_clause_index = segment.segments.index(from_clause_segment)
            from_clause_and_after = segment.segments[from_clause_index:]

            for clause in from_clause_and_after:
                for table_expression in clause.recursive_crawl("table_expression"):
                    table_expression_segments.append(table_expression)
                for column_reference in clause.recursive_crawl("column_reference"):
                    column_reference_segments.append(column_reference)

            return (
                self._lint_aliases_in_join(
                    base_table,
                    table_expression_segments,
                    column_reference_segments,
                    segment,
                )
                or None
            )
        return None

    def _lint_aliases_in_join(
        self, base_table, table_expression_segments, column_reference_segments, segment
    ):
        """Lint and fix all aliases in joins - except for self-joins."""
        # A buffer to keep any violations.
        violation_buff = []

        for table_exp in table_expression_segments:
            table_ref = table_exp.get_child("main_table_expression").get_child(
                "object_reference"
            )

            # If the table_expression has no object_references - skip it
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

            whitespace_ref = table_exp.get_child("whitespace")

            # If there's no alias expression - skip it
            alias_exp_ref = table_exp.get_child("alias_expression")
            if alias_exp_ref is None:
                continue

            alias_identifier_ref = alias_exp_ref.get_child("identifier")
            select_clause = segment.get_child("select_clause")

            ids_refs = []

            # Find all references to alias in select clause
            for alias_with_column in select_clause.recursive_crawl("object_reference"):
                used_alias_ref = alias_with_column.get_child("identifier")
                if used_alias_ref and used_alias_ref.raw == alias_identifier_ref.raw:
                    ids_refs.append(used_alias_ref)

            # Find all references to alias in column references
            for exp_ref in column_reference_segments:
                used_alias_ref = exp_ref.get_child("identifier")
                # exp_ref.get_child('dot') ensures that the column reference includes a table reference
                if (
                    used_alias_ref.raw == alias_identifier_ref.raw
                    and exp_ref.get_child("dot")
                ):
                    ids_refs.append(used_alias_ref)

            # Fixes for deleting ` as sth` and for editing references to aliased tables
            fixes = [
                *[LintFix("delete", d) for d in [alias_exp_ref, whitespace_ref]],
                *[
                    LintFix("edit", alias, alias.edit(table_ref.raw))
                    for alias in [alias_identifier_ref, *ids_refs]
                ],
            ]

            violation_buff.append(
                LintResult(
                    anchor=alias_identifier_ref,
                    description="Avoid using aliases in join condition",
                    fixes=fixes,
                )
            )

        return violation_buff or None
