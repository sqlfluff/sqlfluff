"""Implementation of Rule AM10."""

from collections.abc import Iterator
from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_AM10(BaseRule):
    """INSERT and SELECT specify different numbers of columns.

    Compare an explicit INSERT column list with the SELECT that supplies its
    values. SELECTs containing wildcards are skipped because their column
    counts require schema information. INSERTs without a column list, VALUES
    clauses, and multi-table INSERTs are not checked.

    **Anti-pattern**

    .. code-block:: sql

        INSERT INTO foo (a)
        SELECT a, b FROM bar;

    **Best practice**

    Specify the same number of target columns and SELECT expressions.

    .. code-block:: sql

        INSERT INTO foo (a, b)
        SELECT a, b FROM bar;
    """

    name = "ambiguous.insert_columns"
    groups = ("all", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"insert_statement"})

    @classmethod
    def _source_selects(cls, segment: BaseSegment) -> Iterator[BaseSegment]:
        """Find source SELECTs without entering CTE definitions or subqueries."""
        for child in segment.segments:
            if child.is_type("select_statement"):
                yield child
            elif child.is_type(
                "bracketed", "set_expression", "with_compound_statement"
            ):
                # Name-based set operators can add or discard columns, so the
                # individual SELECT arities do not describe the result.
                if child.is_type("set_expression") and any(
                    keyword.raw_upper in ("NAME", "CORRESPONDING")
                    for operator in child.get_children("set_operator")
                    for keyword in operator.get_children("keyword")
                ):
                    continue
                yield from cls._source_selects(child)

    def _eval(self, context: RuleContext) -> Optional[list[LintResult]]:
        """Compare each explicit source projection to the target column list."""
        segment = context.segment
        # Multi-table INSERTs can map values separately for each target table.
        if any(
            child.is_type("keyword") and child.raw_upper in ("ALL", "FIRST")
            for child in segment.segments
        ):
            return None
        column_list = next(
            (
                child
                for child in segment.get_children("bracketed")
                if child.get_child("column_reference")
            ),
            None,
        )
        if not column_list:
            return None
        target_count = len(column_list.get_children("column_reference"))
        results = []
        for source in self._source_selects(segment):
            select_clause = source.get_child("select_clause")
            assert select_clause
            modifier = select_clause.get_child("select_clause_modifier")
            # BigQuery SELECT AS STRUCT produces a single value, not one per
            # select target. Do not infer its arity from the target list.
            if modifier and "AS" in modifier.raw_upper.split():
                continue
            targets = select_clause.get_children("select_clause_element")
            if any(target.get_child("wildcard_expression") for target in targets):
                continue
            if len(targets) != target_count:
                results.append(
                    LintResult(
                        anchor=select_clause,
                        description=(
                            f"INSERT specifies {target_count} target columns, "
                            f"but SELECT specifies {len(targets)} columns."
                        ),
                    )
                )
        return results or None
