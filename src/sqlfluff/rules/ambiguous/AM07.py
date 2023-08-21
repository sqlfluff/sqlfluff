"""Implementation of Rule AM07."""
from typing import Any, List, Optional, Tuple

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.analysis.select_crawler import (
    Query,
    SelectCrawler,
    WildcardInfo,
    Selectable,
)


class Rule_AM07(BaseRule):
    """Queries within set query produce different numbers of columns.

    **Anti-pattern**

    When writing set expressions, all queries must return the same number of columns.

    .. code-block:: sql

        WITH cte AS (
            SELECT
                a,
                b
            FROM foo
        )
        SELECT * FROM cte
        UNION
        SELECT
            c,
            d,
            e
         FROM t

    **Best practice**

    Always specify columns when writing set queries
    and ensure that they all seleect same number of columns

    .. code-block:: sql

        WITH cte AS (
            SELECT a, b FROM foo
        )
        SELECT
            a,
            b
        FROM cte
        UNION
        SELECT
            c,
            d
        FROM t
    """

    name = "ambiguous.set_columns"
    aliases = ("L068",)
    groups: Tuple[str, ...] = ("all", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"set_expression"}, provide_raw_stack=True)

    def __resolve_wild_query(
        self,
        query: Query,
    ) -> List[Any]:
        """Attempt to resolve the wildcard to a list of selectables."""
        targets = []
        process_queries = query.selectables
        resolved_wildcard = True
        # if one of the source queries for a query within the set is a
        # set expression, just use the first query. If that first query isn't
        # reflective of the others, that will be caught when that segment
        # is processed
        if query.selectables[0].parent:
            if query.selectables[0].parent.is_type("set_expression"):
                process_queries = [query.selectables[0]]

        for selectable in process_queries:
            if selectable.get_wildcard_info():
                for wildcard in selectable.get_wildcard_info():
                    targets += self.__resolve_selectable_wildcard(
                        wildcard, selectable, query
                    )
            else:
                assert selectable.select_info
                targets.extend(
                    [target for target in selectable.select_info.select_targets]
                )

        return targets

    def __resolve_selectable_wildcard(self, wildcard, selectable, root_query):
        # If there is no table specified, it is likely a subquery.
        # Handle that first.
        if not wildcard.tables:
            query_list = SelectCrawler.get(
                root_query, root_query.selectables[0].selectable
            )
            for o in query_list:
                if isinstance(o, Query):
                    return self.__resolve_wild_query(o)
            raise NotImplementedError("I DON'T KNOW HOW TO GET HERE")

        # There might be multiple tables referenced in some wildcard cases.
        # resolved_wildcard = True
        select_list = []
        for wildcard_table in wildcard.tables:
            cte_name = wildcard_table
            # Get the AliasInfo for the table referenced in the wildcard
            # expression.
            alias_info = selectable.find_alias(wildcard_table)
            # attempt to resolve alias or table name to a cte
            if alias_info:
                select_info_target = SelectCrawler.get(
                    root_query, alias_info.from_expression_element
                )[0]
                if isinstance(select_info_target, str):
                    cte_name = select_info_target
                else:
                    select_list += self.__resolve_wild_query(select_info_target)
                    continue

            cte = root_query.lookup_cte(cte_name)
            if cte:
                select_list += self.__resolve_wild_query(cte)
            else:
                # Unable to resolve
                # resolved_wildcard = False
                select_list.append(wildcard)
        return select_list

    def __resolve_selectable(
        self, selectable: Selectable, root_query: Query
    ) -> Tuple[int, bool]:
        assert selectable.select_info
        wildcard_info = selectable.get_wildcard_info()

        # If there's no wildcard, just count the columns and move on.
        if not wildcard_info:
            # if there is no wildcard in the query use the count of select targets
            return len(selectable.select_info.select_targets), True

        select_list = []
        resolved_wildcard = True

        # If the set query contains on or more wildcards, attempt to resolve it to a
        # list of select targets that can be counted.
        for wildcard in wildcard_info:
            select_list += self.__resolve_selectable_wildcard(
                wildcard, selectable, root_query
            )

        # get the number of resolved targets plus the total number of
        # targets minus the number of wildcards
        # if all wildcards have been resolved this adds up to the
        # total number of select targets in the query
        for select in select_list:
            if isinstance(select, WildcardInfo):
                resolved_wildcard = False
        return (
            len(select_list)
            + (len(selectable.select_info.select_targets) - len(wildcard_info)),
            resolved_wildcard,
        )

    def _get_select_target_counts(self, crawler: SelectCrawler):
        """Given a set expression, get the number of select targets in each query."""
        select_target_counts = set()
        assert crawler.query_tree
        resolved_wildcard = True
        # for each selectable in the set
        # , add the number of select targets to a set; in the end
        # length of the set should be one (one size)
        for selectable in crawler.query_tree.selectables:
            cnt, res = self.__resolve_selectable(selectable, crawler.query_tree)
            if not res:
                resolved_wildcard = False
            select_target_counts.add(cnt)

        return (select_target_counts, resolved_wildcard)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """All queries in set expression should return the same number of columns."""
        assert context.segment.is_type("set_expression")
        root = context.segment

        # Is the parent of the set expression a WITH expression?
        # NOTE: Backward slice to work outward.
        for parent in context.parent_stack[::-1]:
            if parent.is_type("with_compound_statement"):
                root = parent
                break

        # Crawl the root.
        crawler = SelectCrawler(
            root,
            context.dialect,
            parent=None,
        )

        set_segment_select_sizes, resolve_wildcard = self._get_select_target_counts(
            crawler
        )
        self.logger.info(
            "Resolved select sizes (resolved wildcard: %s) : %s",
            resolve_wildcard,
            set_segment_select_sizes,
        )
        # if queries had different select target counts
        # and all wildcards have been resolved; fail
        if len(set_segment_select_sizes) > 1 and resolve_wildcard:
            return LintResult(anchor=context.segment)

        return LintResult()
