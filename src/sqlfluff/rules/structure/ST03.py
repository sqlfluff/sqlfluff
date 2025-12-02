"""Implementation of Rule ST03."""

from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.analysis.query import Query


def _is_data_modifying_cte(cte_query: Query) -> bool:
    cte_def = cte_query.cte_definition_segment
    if cte_def is not None:
        try:
            next(
                cte_def.recursive_crawl(
                    "insert_statement",
                    "update_statement",
                    "delete_statement",
                    "merge_statement",
                    recurse_into=False,
                    no_recursive_seg_type=["select_statement"],
                )
            )
            return True
        except StopIteration:
            return False

    raise NotImplementedError("CTE definition is required")  # pragma: no cover


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

        # Some dialects (e.g. Postgres) have data-modifying statements in
        # WITH blocks that are always executed regardless of whether they
        # are referenced by the primary query. Do not flag those as unused.
        # https://github.com/sqlfluff/sqlfluff/issues/7084
        non_data_modifying_ctes = {
            k.upper(): k
            for k, cte in query.ctes.items()
            if not _is_data_modifying_cte(cte)
        }

        # Work through all the references in the file, checking off CTES as the
        # are referenced.
        for reference in context.segment.recursive_crawl("table_reference"):
            non_data_modifying_ctes.pop(reference.raw_normalized(False).upper(), None)

        # For any left un-referenced at the end. Raise an issue about them.
        for name in non_data_modifying_ctes.values():
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
