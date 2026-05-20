"""SQLMesh plugin custom linting rules."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_SM01(BaseRule):
    """Disallow ``1 = 1`` in SQL expressions.

    Models sometimes carry ``WHERE 1 = 1`` placeholders from
    development.  These constant-true predicates should be removed
    before the model is promoted.

    **Anti-pattern**

    .. code-block:: sql

        SELECT *
        FROM orders
        WHERE 1 = 1

    **Best practice**

    Remove the tautology or replace it with a meaningful predicate.

    .. code-block:: sql

        SELECT *
        FROM orders
        WHERE status = 'active'
    """

    name = "sqlmesh.no_one_equal_one"
    aliases = ()
    groups = ("all", "sqlmesh")
    crawl_behaviour = SegmentSeekerCrawler({"comparison_operator"})
    is_fix_compatible = False

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Flag constant true ``1 = 1`` comparisons."""
        if context.segment.raw != "=":
            return None

        if not any(segment.is_type("where_clause") for segment in context.parent_stack):
            return None

        expression = next(
            (
                segment
                for segment in reversed(context.parent_stack)
                if segment.is_type("expression")
            ),
            None,
        )
        if expression is None:
            return None

        lhs, rhs = self._adjacent_operands(expression, context.segment)
        if lhs is None or rhs is None:
            return None

        if lhs.is_templated or rhs.is_templated:
            return None

        if self._is_literal_one(lhs) and self._is_literal_one(rhs):
            return LintResult(
                anchor=context.segment,
                description="Avoid `1 = 1` in production SQL conditions.",
            )

        return None

    @staticmethod
    def _adjacent_operands(
        expression: BaseSegment, operator: BaseSegment
    ) -> tuple[Optional[BaseSegment], Optional[BaseSegment]]:
        """Return nearest non-whitespace segments around an operator."""
        parts = expression.segments
        op_idx = next(
            (idx for idx, segment in enumerate(parts) if segment is operator),
            None,
        )
        if op_idx is None:
            return None, None

        lhs = next(
            (
                parts[idx]
                for idx in range(op_idx - 1, -1, -1)
                if not parts[idx].is_whitespace
            ),
            None,
        )
        rhs = next(
            (
                parts[idx]
                for idx in range(op_idx + 1, len(parts))
                if not parts[idx].is_whitespace
            ),
            None,
        )

        return lhs, rhs

    @staticmethod
    def _is_literal_one(segment: BaseSegment) -> bool:
        """Whether a segment represents the numeric literal ``1``."""
        return segment.is_type("numeric_literal") and segment.raw == "1"


class Rule_SM02(BaseRule):
    """Require explicit type casts for aliased top-level select expressions.

    Every output column should carry an explicit type so downstream consumers
    (and the SQLMesh column-lineage engine) can rely on stable contracts.

    **Anti-pattern**

    .. code-block:: sql

        SELECT amount + fee AS total
        FROM payments

    **Best practice**

    .. code-block:: sql

        SELECT CAST(amount + fee AS DECIMAL(18,2)) AS total
        FROM payments
    """

    name = "sqlmesh.final_select_requires_cast"
    aliases = ()
    groups = ("all", "sqlmesh")
    crawl_behaviour = SegmentSeekerCrawler({"select_clause_element"})
    is_fix_compatible = False

    _cast_function_names = {"CAST", "TRY_CAST", "SAFE_CAST", "CONVERT"}

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Ensure aliased top-level select expressions include explicit cast."""
        segment = context.segment

        if self._is_nested_select(context):
            return None

        alias_expression = segment.get_child("alias_expression")
        if alias_expression is None:
            return None

        if segment.get_child("wildcard_expression") is not None:
            return None

        projected_segment = self._get_projected_segment(segment)
        if projected_segment and self._is_top_level_cast(projected_segment):
            return None

        return LintResult(
            anchor=alias_expression,
            description=(
                "Aliased top-level select expressions must use explicit type "
                "casting (for example CAST(... AS ...))."
            ),
        )

    @staticmethod
    def _is_nested_select(context: RuleContext) -> bool:
        """Whether current select element is inside a nested select statement."""
        return (
            sum(
                1
                for segment in context.parent_stack
                if segment.is_type("select_statement")
            )
            > 1
        )

    @staticmethod
    def _get_projected_segment(segment: BaseSegment) -> Optional[BaseSegment]:
        """Return the top-level projected expression before the alias."""
        return next(
            (
                child
                for child in segment.segments
                if not child.is_meta
                and not child.is_whitespace
                and not child.is_type("alias_expression")
            ),
            None,
        )

    def _is_top_level_cast(self, segment: BaseSegment) -> bool:
        """Whether the final projected expression is explicitly cast."""
        if segment.is_type("cast_expression"):
            return True

        if segment.is_type("function"):
            function_name = segment.get_child("function_name")
            return (
                function_name is not None
                and function_name.raw_upper in self._cast_function_names
            )

        if segment.is_type("expression"):
            code_children = [
                child
                for child in segment.segments
                if not child.is_meta and not child.is_whitespace
            ]
            return len(code_children) == 1 and self._is_top_level_cast(code_children[0])

        return False


class Rule_SM03(BaseRule):
    """Disallow references to the ``AD_HOC`` database."""

    name = "sqlmesh.no_adhoc_catalog"
    aliases = ()
    groups = ("all", "sqlmesh")
    crawl_behaviour = SegmentSeekerCrawler({"table_reference"})
    is_fix_compatible = False

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Flag table references using AD_HOC as catalog name."""
        if not context.segment.is_type("table_reference"):
            return None

        identifiers = [
            seg
            for seg in context.segment.segments
            if seg.is_type("identifier", "naked_identifier", "quoted_identifier")
        ]

        if len(identifiers) < 2:
            return None

        catalog = identifiers[0]
        if catalog.raw_normalized().strip('"`[]').upper() == "AD_HOC":
            return LintResult(
                anchor=catalog,
                description="References to AD_HOC catalog are not allowed.",
            )

        return None
