"""Implementation of Rule RF07."""

from sqlfluff.core.dialects.common import qualification
from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.analysis.select import get_select_statement_info


class Rule_RF07(BaseRule):
    """Do not reference a column alias inside its own ``OVER`` clause.

    Window functions are evaluated before the ``SELECT`` list aliases are
    applied, so an unqualified reference in a ``PARTITION BY`` or ``ORDER BY``
    which happens to match an alias does not resolve to that alias. When more
    than one table is in scope it silently resolves to a real column on one of
    them instead, changing the result without any error.

    **Anti-pattern**

    ``id`` is an alias for ``t1.col1``, but inside the window it resolves to
    ``t2.id`` from the joined table.

    .. code-block:: sql

        SELECT
            t1.col1 AS id,
            ROW_NUMBER() OVER (PARTITION BY id ORDER BY t1.ts) AS rn
        FROM t1
        LEFT JOIN t2 ON t1.col1 = t2.id

    **Best practice**

    Qualify the reference with its table so the intended column is used.

    .. code-block:: sql

        SELECT
            t1.col1 AS id,
            ROW_NUMBER() OVER (PARTITION BY t1.col1 ORDER BY t1.ts) AS rn
        FROM t1
        LEFT JOIN t2 ON t1.col1 = t2.id
    """

    name = "references.window_alias"
    groups = ("all", "references")
    crawl_behaviour = SegmentSeekerCrawler({"over_clause"})

    def _eval(self, context: RuleContext) -> EvalResultType:
        select_statement = None
        for parent in reversed(context.parent_stack):
            if parent.is_type("select_statement"):
                select_statement = parent
                break
        if select_statement is None:  # pragma: no cover
            return None

        select_info = get_select_statement_info(select_statement, context.dialect)
        # Only relevant when the alias could collide with a column on another
        # table, i.e. when more than one table is referenced.
        if not select_info or len(select_info.table_aliases) <= 1:
            return None

        # Names of the aliases declared in this SELECT. Matched by raw spelling,
        # consistent with how RF02 compares column aliases.
        alias_names = {c.alias_identifier_name for c in select_info.col_aliases}
        if not alias_names:
            return None

        results: list[LintResult] = []
        for clause in context.segment.recursive_crawl(
            "partitionby_clause", "orderby_clause"
        ):
            for reference in clause.recursive_crawl(
                "column_reference", no_recursive_seg_type="select_statement"
            ):
                if qualification(reference, context.dialect.name) != "unqualified":
                    continue
                if reference.raw in alias_names:
                    results.append(
                        LintResult(
                            anchor=reference,
                            description=(
                                f"Reference {reference.raw!r} in window clause "
                                "matches a select alias but resolves to a table "
                                "column. Qualify it with its table."
                            ),
                        )
                    )
        return results or None
