"""Implementation of Rule AM09."""


from sqlfluff.utils.analysis.query import Query
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_AM09(BaseRule):
    """Ensures all tables are referenced with schemas.

    **Anti-pattern**

    A table is referenced without a schema.

    .. code-block:: sql

        SELECT
            a,
            b
        FROM my_table

    **Best practice**

    Always fully qualify tables.

    .. code-block:: sql

        SELECT
            a,
            b
        FROM my_schema.my_table
    """

    name = "ambiguous.explicit_schema"
    aliases = ()
    is_fix_compatible = False
    groups: tuple[str, ...] = ("all", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"table_reference"})

    def _collect_cte_names(self, ctes, visited=None):
        if visited is None:
            visited = set()
        names = set()
        for query in ctes:
            qid = id(query)
            if qid in visited:
                continue
            visited.add(qid)
            if hasattr(query, 'cte_name_segment') and query.cte_name_segment is not None:
                name = getattr(query.cte_name_segment, 'raw', None)
                if name:
                    names.add(name.lower())
            if hasattr(query, 'ctes') and query.ctes:
                names.update(self._collect_cte_names(
                    query.ctes.values(), visited))
        return names

    def _collect_parent_cte_names(self, query, visited=None):
        if visited is None:
            visited = set()
        names = set()
        parent = getattr(query, 'parent', None)
        while parent is not None:
            qid = id(parent)
            if qid in visited:
                break
            visited.add(qid)
            if hasattr(parent, 'ctes') and parent.ctes:
                names.update(self._collect_cte_names(
                    parent.ctes.values(), visited))
            parent = getattr(parent, 'parent', None)
        return names

    def _eval(self, context: RuleContext):
        """Tables must be schema-qualified."""
        # A table reference is schema-qualified if it contains a dot.
        if "." in context.segment.raw:
            return None
        with_segment = next(
            (x for x in context.parent_stack if x.type == "with_compound_statement"), None)
        if with_segment is None:
            return LintResult(
                anchor=context.segment,
                description=f"Table `{context.segment.raw}` is not schema-qualified. Please use Explicit Schema Name.",
            )
        query: Query = Query.from_segment(with_segment, context.dialect)
        ctes = query.ctes.values()

        # Collect CTE names from children
        cte_names = self._collect_cte_names(ctes)
        # Collect CTE names from parents (if any cte object exists)
        for query in ctes:
            cte_names.update(self._collect_parent_cte_names(query))

        if context.segment.raw.lower() in cte_names:
            return None

        return LintResult(
            anchor=context.segment,
            description=f"Table `{context.segment.raw}` is not schema-qualified. Please use Explicit Schema Name.",
        )
