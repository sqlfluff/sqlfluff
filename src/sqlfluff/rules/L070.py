"""Implementation of Rule L070."""
from typing import Optional

from sqlfluff.utils.analysis.select_crawler import Query, SelectCrawler, WildcardInfo
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_groups


@document_groups
class Rule_L070(BaseRule):
    """Queries within set query produce different numbers of columns.

    **Anti-pattern**

    When writing set expressions
    , all queries must return the
    same number of columns

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

    groups = ("all",)
    crawl_behaviour = SegmentSeekerCrawler({"set_expression"}, provide_raw_stack=True)

    def _find_all_ctes_utils(self, query, cte_dict):
        """Generate a list of all ctes in a query."""
        # cte_dict = cte_dict | query.ctes
        cte_dict.update(query.ctes)
        for cte_name, cte in query.ctes.items():
            cte_dict = self._find_all_ctes_utils(cte, cte_dict)
        return cte_dict

    def _find_all_ctes(self, context: RuleContext, cte_dict):
        for seg in context.parent_stack:
                    if  not seg.is_type("common_table_expression"):
                        parent_query = SelectCrawler(
                            seg, context.dialect
                ).query_tree
                cte_dict.update(self._find_all_ctes_utils(parent_query, cte_dict))

        return cte_dict

    def __resolve_wildcard(
        self,
        context: RuleContext,
        query,
        parent_query,
        resolve_targets,
        all_ctes,
    ):
        """Attempt to resolve the wildcard to a list of selectables."""
        process_queries = query.selectables
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
                    if wildcard.tables:
                        for wildcard_table in wildcard.tables:
                            alias_info = selectable.find_alias(wildcard_table)
                            # attempt to resolve alias or table name to a cte;
                            if alias_info:
                                select_info_target = SelectCrawler.get(
                                    parent_query, alias_info.from_expression_element
                                )[0]
                                if isinstance(select_info_target, str):
                                    cte = None
                                    # handles case where cte is in subquery
                                    cte_child = query.lookup_cte(select_info_target)
                                    if select_info_target.upper() in all_ctes:
                                        cte = all_ctes[select_info_target.upper()]
                                    # check parent cte
                                    if cte:
                                        self.__resolve_wildcard(
                                            context,
                                            cte,
                                            parent_query,
                                            resolve_targets,
                                            all_ctes,
                                        )
                                    elif cte_child:
                                        self.__resolve_wildcard(
                                            context,
                                            cte_child,
                                            parent_query,
                                            resolve_targets,
                                            all_ctes,
                                        )
                                    else:
                                        resolve_targets.append(wildcard)

                                # if select_info_target is not a string
                                # , process as a subquery
                                else:
                                    self.__resolve_wildcard(
                                        context,
                                        select_info_target,
                                        parent_query,
                                        resolve_targets,
                                        all_ctes,
                                    )
                            else:
                                cte = None
                                cte_child = query.lookup_cte(wildcard_table)
                                if wildcard_table.upper() in all_ctes:
                                    cte = all_ctes[wildcard_table.upper()]
                                if cte:
                                    self.__resolve_wildcard(
                                        context,
                                        cte,
                                        parent_query,
                                        resolve_targets,
                                        all_ctes,
                                    )
                                elif cte_child:
                                    self.__resolve_wildcard(
                                        context,
                                        cte_child,
                                        parent_query,
                                        resolve_targets,
                                        all_ctes,
                                    )
                                else:
                                    resolve_targets.append(wildcard)
                    # if there is no table specified, it is likely a subquery
                    else:
                        query_list = SelectCrawler.get(
                            query, query.selectables[0].selectable
                        )
                        for o in query_list:
                            if isinstance(o, Query):
                                self.__resolve_wildcard(
                                    context, o, parent_query, resolve_targets, all_ctes
                                )
                                return resolve_targets
            else:
                resolve_targets.extend(
                    [target for target in selectable.select_info.select_targets]
                )

        return resolve_targets

    def _get_select_target_counts(self, context: RuleContext, crawler):
        """Given a set expression, get the number of select targets in each query."""
        select_list = None
        select_target_counts = set()
        set_selectables = crawler.query_tree.selectables
        resolved_wildcard = True
        parent_crawler = SelectCrawler(context.parent_stack[0], context.dialect)
        # for each selectable in the set
        # , add the number of select targets to a set; in the end
        # length of the set should be one (one size)
        for selectable in set_selectables:
            # if the set query contains a wildcard
            # , attempt to resolve wildcard to a list of
            # select targets that can be counted
            if selectable.get_wildcard_info():
                # to start, get a list of all of the ctes in the parent
                # stack to check whether they resolve to wildcards

                all_cte_queries = self._find_all_ctes(context, {})
                select_crawler = SelectCrawler(
                    selectable.selectable, context.dialect
                ).query_tree

                select_list = self.__resolve_wildcard(
                    context,
                    select_crawler,
                    parent_crawler.query_tree,
                    [],
                    all_cte_queries,
                )

                # get the number of resolved targets plus the total number of
                # targets minus the number of wildcards
                # if all wildcards have been resolved this adds up to the
                # total number of select targets in the query
                select_target_counts.add(
                    len(select_list)
                    + (
                        len(selectable.select_info.select_targets)
                        - len(selectable.get_wildcard_info())
                    )
                )
                for select in select_list:
                    if isinstance(select, WildcardInfo):
                        resolved_wildcard = False
            else:
                # if there is no wildcard in the query use the count of select targets
                select_list = selectable.select_info.select_targets
                select_target_counts.add(len(select_list))

        return (select_target_counts, resolved_wildcard)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """All queries in set expression should return the same number of columns."""
        assert context.segment.is_type("set_expression")
        crawler = SelectCrawler(context.segment, context.dialect)

        set_segment_select_sizes, resolve_wildcard = self._get_select_target_counts(
            context, crawler
        )
        # if queries had different select target counts
        # and all wildcards have been resolved; fail
        if len(set_segment_select_sizes) > 1 and resolve_wildcard:
            return LintResult(anchor=context.segment)

        return LintResult()
