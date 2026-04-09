"""Implementation of Rule RF07."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_RF07(BaseRule):
    """CLUSTER BY columns must match column definitions in CREATE TABLE.

    When a ``CREATE TABLE`` statement includes both explicit column definitions
    and a ``CLUSTER BY`` clause, every column referenced in ``CLUSTER BY`` must
    appear in the column definitions. A mismatch usually indicates a typo that
    would fail at runtime.

    .. note::
       This rule only applies when the ``CREATE TABLE`` statement contains
       explicit column definitions. Statements that derive their schema from
       a query (``CREATE TABLE ... AS SELECT``) are not checked because the
       resulting column names are not statically visible in the DDL.

    **Anti-pattern**

    In this example, ``col2`` is referenced in ``CLUSTER BY`` but is not
    defined in the table's column list.

    .. code-block:: sql

        CREATE TABLE my_table (
            col1 STRING
        )
        CLUSTER BY (col2)

    **Best practice**

    Ensure the ``CLUSTER BY`` columns match the column definitions.

    .. code-block:: sql

        CREATE TABLE my_table (
            col1 STRING
        )
        CLUSTER BY (col1)

    """

    name = "references.cluster_by_columns"
    groups = ("all", "references")
    crawl_behaviour = SegmentSeekerCrawler({"create_table_statement"})
    is_fix_compatible = False

    @staticmethod
    def _normalise_identifier(col_ref: BaseSegment) -> str:
        """Extract and normalise an identifier from a column_reference.

        Strips surrounding quotes (backticks, double-quotes) so that
        quoted and unquoted references to the same column compare equal.
        """
        raw = col_ref.raw
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("`", '"'):
            raw = raw[1:-1]
        return raw.upper()

    def _eval(self, context: RuleContext) -> Optional[list[LintResult]]:
        """Validate CLUSTER BY columns against column definitions."""
        assert context.segment.is_type("create_table_statement")

        # Collect defined column names from column_definition segments.
        defined_columns: set[str] = set()
        for col_def in context.segment.recursive_crawl("column_definition"):
            # The first column_reference inside a column_definition is the
            # column name itself.
            col_ref = next(col_def.recursive_crawl("column_reference"), None)
            if col_ref is not None:
                defined_columns.add(self._normalise_identifier(col_ref))

        # If there are no explicit column definitions (e.g. CTAS), skip.
        if not defined_columns:
            return None

        # Find CLUSTER BY clauses and validate their column references.
        results: list[LintResult] = []
        for cluster_clause in context.segment.recursive_crawl(
            "table_cluster_by_clause"
        ):
            for col_ref in cluster_clause.recursive_crawl("column_reference"):
                if self._normalise_identifier(col_ref) not in defined_columns:
                    results.append(
                        LintResult(
                            anchor=col_ref,
                            description=(
                                f"Column '{col_ref.raw}' in CLUSTER BY "
                                f"is not defined in the table's column list."
                            ),
                        )
                    )

        return results or None
