"""Implementation of Rule AM10."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.analysis.query import SELECTABLE_TYPES


class Rule_AM10(BaseRule):
    """INSERT target and SELECT have different numbers of columns.

    **Anti-pattern**

    An explicit INSERT column list must match the number of columns returned
    by its SELECT source.

    .. code-block:: sql

        INSERT INTO destination (a)
        SELECT x, y FROM source;

    **Best practice**

    Specify matching target and source columns.

    .. code-block:: sql

        INSERT INTO destination (a, b)
        SELECT x, y FROM source;

    Statements without an explicit target column list, or with wildcard
    projections, are not checked. This rule does not expand wildcards, including
    those referencing CTEs. It checks the outer projection, not columns inside
    CTE definitions, scalar subqueries or FROM subqueries.
    BigQuery SELECT AS STRUCT produces one column, including with a wildcard.

    Multi-table INSERT, partition mappings and REPLACE USING clauses use
    different column bindings and are not checked. DuckDB COLUMNS and UNNEST
    expressions are also skipped because their output width may be unknown.
    No automatic fix is offered because the intended columns cannot be inferred.
    """

    name = "ambiguous.insert_columns"
    groups = ("all", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"insert_statement"})

    @staticmethod
    def _select_source(segment: BaseSegment) -> Optional[BaseSegment]:
        """Unwrap parentheses without searching inside unrelated expressions."""
        while segment.is_type("bracketed"):
            child = segment.get_child("bracketed", *SELECTABLE_TYPES)
            if not child:
                return None
            segment = child
        return segment if segment.is_type(*SELECTABLE_TYPES) else None

    @staticmethod
    def _select_count(select_clause: BaseSegment, dialect: str) -> Optional[int]:
        """Count a statically known projection without descending into subqueries."""
        modifier = select_clause.get_child("select_clause_modifier")
        if dialect == "bigquery" and modifier:
            # SELECT AS STRUCT produces one value, even when it contains '*'.
            if any(seg.raw_upper == "STRUCT" for seg in modifier.segments):
                return 1

        targets = select_clause.get_children("select_clause_element")
        if not targets or any(
            target.get_child("wildcard_expression", "composite_value_expansion")
            for target in targets
        ):
            return None

        if dialect == "duckdb":
            for target in targets:
                for function in target.recursive_crawl(
                    "function", no_recursive_seg_type="select_statement"
                ):
                    name = function.get_child("function_name")
                    if name:
                        function_name = "".join(
                            seg.raw_normalized(False)
                            for seg in name.raw_segments
                            if seg.is_code
                        ).upper()
                        if function_name in {"COLUMNS", "*COLUMNS", "UNNEST"}:
                            return None
        return len(targets)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Compare explicit targets with their immediate SELECT source."""
        target_count = 0
        source = None
        for segment in context.segment.segments:
            # These clauses do not bind a plain target list to the SELECT.
            if segment.is_type("keyword") and segment.raw_upper in {
                "ALL",
                "FIRST",
                "PARTITION",
                "USING",
                "DEFAULT",
                "RETURNING",
            }:
                return None
            if segment.is_type("values_clause"):
                return None
            source = self._select_source(segment)
            if source:
                break
            if segment.is_type("bracketed"):
                target_count = len(segment.get_children("column_reference"))

        if not target_count or not source:
            return None
        if "unparsable" in source.descendant_type_set:
            return None

        counts = []
        for select in source.recursive_crawl(
            "select_statement",
            recurse_into=False,
            no_recursive_seg_type="common_table_expression",
        ):
            select_clause = select.get_child("select_clause")
            if not select_clause:
                # For example, DuckDB's FROM-first implicit SELECT *.
                return None
            count = self._select_count(select_clause, context.dialect.name)
            if count is None:
                return None
            counts.append((select_clause, count))

        for select_clause, count in counts:
            if count != target_count:
                return LintResult(
                    anchor=select_clause,
                    description=(
                        f"INSERT target column count ({target_count}) does not match "
                        f"SELECT column count ({count})."
                    ),
                )
        return None
