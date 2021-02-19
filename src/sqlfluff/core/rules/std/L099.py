"""Implementation of Rule L099."""
from typing import List, NamedTuple, Optional

from sqlfluff.core.rules.base import BaseCrawler, LintResult
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.rules.std import L020


class WildcardInfo(NamedTuple):
    segment: BaseSegment
    table: Optional[str]


class Rule_L099(BaseCrawler):
    """Query produces an unknown number of result columns.

    | **Anti-pattern**
    | Querying all columns using `*` produces a query result where the number
    | or ordering of columns may vary due to schema changes in upstream data
    | sources. This should be avoided because it is prone to breakage in
    | production.

    .. code-block::

        WITH cte AS (
            SELECT * FROM foo
        )

        SELECT * FROM cte

    | **Best practice**
    | Somewhere along the "path" to the source data, specify columns explicitly.

    .. code-block::

        WITH cte AS (
            SELECT * FROM foo
        )

        SELECT a, b FROM cte

    """

    _works_on_unparsable = False

    # with_compound_statement
    #   common_table_expression
    #     select_statement
    #       select_clause
    #         select_target_element
    #   common_table_expression ...
    #   select_statement
    #     select_clause
    #       select_target_element

    @classmethod
    def _get_wildcard_info(cls, select_info: L020.SelectStatementColumnsAndTables) -> List[WildcardInfo]:
        buff = []
        for seg in select_info.select_targets:
            if seg.get_child('wildcard_expression'):
                if '.' in seg.raw:
                    table =seg.raw.rsplit('.', 1)[0]
                else:
                    if len(select_info.table_aliases) == 1:
                        # Unqualified '*' and there is only one table, so that
                        # must be the table. Probably need to revisit this to
                        # reconcile/consider alias vs actual table name.
                        table = select_info.table_aliases[0].ref_str
                    else:
                        table = None
                buff.append(WildcardInfo(seg, table))
        return buff

    def _eval(self, segment, **kwargs):
        """Outermost query should produce known number of columns.
        """
        if segment.is_type("statement"):
            queries = {}

            # Get all the select statements, then get the path to each to determine
            # the structure.
            for select_statement in segment.recursive_crawl("select_statement"):
                path_to = segment.path_to(select_statement)

                # If it's a CTE, get the name and info on the query inside.
                cte = None
                for seg in path_to:
                    if seg.is_type("common_table_expression"):
                        cte = seg
                        break
                select_name = cte.segments[0].raw if cte else None
                select_info = L020.Rule_L020.get_select_statement_info(select_statement, kwargs.get('dialect'), early_exit=False)
                queries[select_name] = select_info

            # Walk from the final query (key=None) to any wildcard columns
            # in the select targets. If it's wildcards all the way, warn.
            select_info = queries[None]
            while True:
                wildcards = self._get_wildcard_info(select_info)
                if not wildcards:
                    return None
                wildcard = wildcards[0]
                # TODO: Loop or recurse here since a select may have multiple
                # wildcards in its select targets.
                #for wildcard in wildcards:
                select_info = queries.get(wildcard.table)
                if not select_info:
                    # References something that is not a CTE. Assume it's
                    # an external table, one we can't check. Thus, warn.
                    return LintResult(anchor=queries[None].select_statement)
        return None
