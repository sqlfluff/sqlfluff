"""Implementation of Rule ST03."""

from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.analysis.query import Query


class Rule_ST03(BaseRule):
    """Query defines a CTE (common-table expression) but does not use it.

    **Anti-pattern**

    Defining a CTE that is not used by the query is harmless, but it means
    the code is unnecessary and could be removed.

    .. code-block:: sql

        WITH cte1 AS (
          SELECT a
          FROM t
        ),
        cte2 AS (
          SELECT b
          FROM u
        )

        SELECT *
        FROM cte1

    **Best practice**

    Remove unused CTEs.

    .. code-block:: sql

        WITH cte1 AS (
          SELECT a
          FROM t
        )

        SELECT *
        FROM cte1
    """

    name = "structure.unused_cte"
    aliases = ("L045",)
    groups = ("all", "core", "structure")
    crawl_behaviour = SegmentSeekerCrawler({"with_compound_statement"})

    def _eval(self, context: RuleContext) -> EvalResultType:
        result = []
        query: Query = Query.from_root(context.segment, dialect=context.dialect)

        # Build up a dict of remaining CTEs (uppercased as not case sensitive).
        remaining_ctes = {k.upper(): k for k in query.ctes.keys()}

        # Work through all the references in the file, checking off CTES as the
        # are referenced. We don't recurse inside inner WITH statements.
        for reference in context.segment.recursive_crawl(
            "table_reference", no_recursive_seg_type="with_compound_statement"
        ):
            remaining_ctes.pop(reference.raw.upper(), None)

        # For any left un-referenced at the end. Raise an issue about them.
        for name in remaining_ctes.values():
            cte = query.ctes[name]
            result += [
                LintResult(
                    anchor=cte.cte_name_segment,
                    description=f"Query defines CTE "
                    f'"{cte.cte_name_segment.raw}" '
                    f"but does not use it.",
                )
            ]
        return result
