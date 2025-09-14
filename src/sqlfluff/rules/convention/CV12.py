"""Implementation of Rule CV12."""

import collections
from collections.abc import Iterator
from typing import Deque

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.parser.segments.common import (
    BinaryOperatorSegment,
    WhitespaceSegment,
)
from sqlfluff.core.parser.segments.keyword import KeywordSegment
from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.fix import LintFix
from sqlfluff.dialects.dialect_ansi import (
    ExpressionSegment,
    JoinClauseSegment,
    JoinOnConditionSegment,
)


class Rule_CV12(BaseRule):
    """Use `JOIN ... ON ...` instead of `WHERE ...` for join conditions.

    **Anti-pattern**

    Using WHERE clause for join conditions.

    .. code-block:: sql

        SELECT
            foo.a
            , bar.b
        FROM foo
        JOIN bar
        WHERE foo.x = bar.y;

    **Best practice**

    Use JOIN ON clause for join condition.

    .. code-block:: sql

        SELECT
            foo.a
            , bar.b
        FROM foo
        JOIN bar
        ON foo.x = bar.y;

    """

    name = "convention.join_condition"
    aliases = ()
    groups = ("all", "convention")
    crawl_behaviour = SegmentSeekerCrawler({"select_statement"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Find joins with WHERE clause.

        Fix them into JOIN ON.
        """
        return [lint_result for lint_result in self._eval_gen(context)]

    def _eval_gen(self, context: RuleContext) -> Iterator[LintResult]:
        # We are only interested in SELECT statement.
        select_statement = context.segment
        assert select_statement.is_type("select_statement")

        maybe_where_clause = select_statement.get_child("where_clause")
        if not maybe_where_clause:
            return

        where_clause = maybe_where_clause
        where_clause_simplifable = self._is_where_clause_simplifable(where_clause)

        if where_clause_simplifable:
            expr = where_clause.get_child("expression")
            assert expr is not None
            subexpressions = self._get_subexpression_chunks(expr)
        else:
            subexpressions = []
        consumed_subexpressions = set()

        # get references in from clause
        select_table_references = [
            *select_statement.recursive_crawl(
                "from_expression_element",
                no_recursive_seg_type=["join_clause", "select_statement"],
            )
        ]

        # track all seen references (from clause + all previous joins)
        encountered_references = {
            self._get_from_expression_element_alias(table_ref)
            for table_ref in select_table_references
        }

        for join_clause in select_statement.recursive_crawl(
            "join_clause", no_recursive_seg_type=["select_statement"]
        ):
            # mark table reference as seen
            join_table_reference = next(
                join_clause.recursive_crawl(
                    "from_expression_element",
                    no_recursive_seg_type=["select_statement"],
                )
            )
            encountered_references.add(
                self._get_from_expression_element_alias(join_table_reference)
            )
            join_clause_keywords = [
                seg for seg in join_clause.segments if seg.type == "keyword"
            ]

            if any(
                kw.raw_upper in ("CROSS", "POSITIONAL", "USING", "APPLY")
                for kw in join_clause_keywords
            ):
                # If explicit CROSS JOIN is used, disregard lack of condition
                # If explicit POSITIONAL JOIN is used, disregard lack of condition
                # If explicit JOIN USING is used, disregard lack of condition
                # If explicit CROSS/OUTER APPLY is used, disregard lack of condition
                continue

            this_join_condition = join_clause.get_child("join_on_condition")
            if this_join_condition:
                # Join condition is present, no error reported.
                continue

            if not where_clause_simplifable:
                yield LintResult(anchor=join_clause)
            else:
                this_join_clause_subexpressions = set()
                for subexpr_idx, subexpr_segments in enumerate(subexpressions):
                    if subexpr_idx in consumed_subexpressions:
                        continue
                    qualified_column_references = [
                        col_ref
                        for seg in subexpr_segments
                        for col_ref in seg.recursive_crawl(
                            "column_reference",
                            no_recursive_seg_type="select_statement",
                        )
                        if "dot" in col_ref.descendant_type_set
                    ]
                    if len(qualified_column_references) > 1 and all(
                        col_ref.raw_upper.startswith(
                            tuple(
                                f"{table_ref}." for table_ref in encountered_references
                            )
                        )
                        for col_ref in qualified_column_references
                    ):
                        this_join_clause_subexpressions.add(subexpr_idx)
                        consumed_subexpressions.add(subexpr_idx)

                if not this_join_clause_subexpressions:
                    yield LintResult(join_clause)
                else:
                    join_clause_fix_segments: Deque[BaseSegment] = collections.deque()
                    for subexpr_idx, subexpr_segments in enumerate(subexpressions):
                        if subexpr_idx in this_join_clause_subexpressions:
                            join_clause_fix_segments.extend(subexpr_segments)
                            join_clause_fix_segments.append(
                                BinaryOperatorSegment("AND")
                            )

                    while join_clause_fix_segments and join_clause_fix_segments[
                        0
                    ].is_type("whitespace", "binary_operator"):
                        join_clause_fix_segments.popleft()
                    while join_clause_fix_segments and join_clause_fix_segments[
                        -1
                    ].is_type("whitespace", "binary_operator"):
                        join_clause_fix_segments.pop()

                    join_on_expression = ExpressionSegment(
                        tuple(join_clause_fix_segments),
                    )
                    join_on = JoinOnConditionSegment(
                        (
                            KeywordSegment("ON"),
                            WhitespaceSegment(),
                            join_on_expression,
                        )
                    )
                    join_clause_segment = JoinClauseSegment(
                        (
                            *join_clause.segments,
                            WhitespaceSegment(),
                            join_on,
                        )
                    )

                    yield LintResult(
                        anchor=join_clause,
                        fixes=[
                            LintFix.replace(
                                join_clause,
                                edit_segments=[join_clause_segment],
                            )
                        ],
                    )

        if not where_clause_simplifable:
            return

        if not consumed_subexpressions:
            return

        # Rewrite WHERE to keep conditions not moved to ON clauses
        where_clause_fix_segments: Deque[BaseSegment] = collections.deque()
        for subexpr_idx, subexpr_segments in enumerate(subexpressions):
            if subexpr_idx not in consumed_subexpressions:
                where_clause_fix_segments.extend(subexpr_segments)
                where_clause_fix_segments.append(BinaryOperatorSegment("AND"))

        while where_clause_fix_segments and where_clause_fix_segments[0].is_type(
            "whitespace", "binary_operator"
        ):
            where_clause_fix_segments.popleft()
        while where_clause_fix_segments and where_clause_fix_segments[-1].is_type(
            "whitespace", "binary_operator"
        ):
            where_clause_fix_segments.pop()

        if where_clause_fix_segments:
            where_clause_expr = where_clause.get_child("expression")
            assert where_clause_expr is not None
            yield LintResult(
                anchor=where_clause_expr,
                fixes=[
                    LintFix.replace(
                        where_clause_expr, edit_segments=[*where_clause_fix_segments]
                    )
                ],
            )
        else:
            assert select_statement.segments[-1].is_type("where_clause")
            assert select_statement.segments[-2].is_type("whitespace", "newline")
            yield LintResult(
                anchor=where_clause,
                fixes=[
                    LintFix.delete(select_statement.segments[-2]),
                    LintFix.delete(select_statement.segments[-1]),
                ],
            )

    @staticmethod
    def _get_from_expression_element_alias(from_expr_element: BaseSegment) -> str:
        if "alias_expression" in from_expr_element.direct_descendant_type_set:
            alias_seg = from_expr_element.get_child("alias_expression")
            assert alias_seg is not None
            identifier_seg = alias_seg.get_child("identifier")
            assert identifier_seg is not None
            alias_str = identifier_seg.raw_upper
        else:
            alias_str = from_expr_element.raw_upper

        return alias_str

    @staticmethod
    def _is_where_clause_simplifable(where_clause: BaseSegment) -> bool:
        assert where_clause.is_type("where_clause")
        expr = where_clause.get_child("expression")
        if not expr:  # pragma: no cover
            # According to grammar, we should always have an ExpressionSegment
            # See sqlfluff.dialects.dialect_ansi.WhereClauseSegment
            return False
        ops = expr.recursive_crawl("binary_operator")
        return all(op.raw_upper == "AND" for op in ops)

    @staticmethod
    def _get_subexpression_chunks(expr: BaseSegment) -> list[list[BaseSegment]]:
        expr_segments = expr.segments
        bin_op_indices = [
            i for i, e in enumerate(expr_segments) if e.is_type("binary_operator")
        ]
        split_segments = [None, *[expr_segments[i] for i in bin_op_indices], None]
        start_segments_iter = iter(split_segments)
        stop_segments_iter = iter(split_segments)
        _ = next(stop_segments_iter)
        return [
            expr.select_children(start_seg, stop_seg)
            for start_seg, stop_seg in zip(start_segments_iter, stop_segments_iter)
        ]
