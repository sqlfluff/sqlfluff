"""Implementation of Rule RF08."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler

# Databricks and Spark parse this as `table_cluster_by_clause`; BigQuery uses
# `cluster_by_segment`. The contents are the same shape in both.
_CLUSTER_CLAUSES = ("table_cluster_by_clause", "cluster_by_segment")
_IDENTIFIERS = ("naked_identifier", "quoted_identifier")


def _name_of(segment: BaseSegment) -> Optional[str]:
    """The identifier a column definition or reference introduces, case folded."""
    part = next(segment.recursive_crawl(*_IDENTIFIERS), None)
    return part.raw.strip('"`[]').upper() if part else None


class Rule_RF08(BaseRule):
    """``CLUSTER BY`` should only reference columns defined by the table.

    A clustering column that is not in the table definition is accepted by the
    parser but rejected by the engine when the statement runs, so a typo here
    survives linting and fails at execution time.

    Only ``CREATE TABLE`` statements that declare their columns explicitly are
    checked. A ``CREATE TABLE ... AS SELECT`` takes its columns from the query,
    so it is left alone even when it also carries a column list.

    **Anti-pattern**

    ``CLUSTER BY`` names a column the table does not have.

    .. code-block:: sql
       :force:

        CREATE TABLE my_table (
            col1 STRING
        )
        CLUSTER BY (col2);

    **Best practice**

    Cluster by a column the table defines.

    .. code-block:: sql
       :force:

        CREATE TABLE my_table (
            col1 STRING
        )
        CLUSTER BY (col1);
    """

    name = "references.cluster_by"
    groups = ("all", "references")
    crawl_behaviour = SegmentSeekerCrawler({"create_table_statement"})

    def _eval(self, context: RuleContext) -> Optional[list[LintResult]]:
        """Compare the clustering columns against the defined ones."""
        assert context.segment.is_type("create_table_statement")

        cluster_clauses = list(context.segment.recursive_crawl(*_CLUSTER_CLAUSES))
        if not cluster_clauses:
            return None

        # A statement with a query takes its columns from that query, so an
        # explicit column list is not necessarily the whole story and comparing
        # against it can flag a column the SELECT does provide. Skip any CTAS,
        # with or without a column list.
        if any(
            context.segment.recursive_crawl(
                "select_statement", "with_compound_statement"
            )
        ):
            return None

        defined = {
            name
            for definition in context.segment.recursive_crawl("column_definition")
            if (name := _name_of(definition)) is not None
        }
        # No explicit column list means CTAS or CREATE TABLE LIKE, where the
        # columns come from elsewhere and cannot be checked here.
        if not defined:
            return None

        results = []
        for clause in cluster_clauses:
            for reference in clause.recursive_crawl("column_reference"):
                name = _name_of(reference)
                if name is not None and name not in defined:
                    results.append(
                        LintResult(
                            anchor=reference,
                            description=(
                                f"Column '{reference.raw}' in CLUSTER BY is not "
                                "defined by this table."
                            ),
                        )
                    )

        return results or None
