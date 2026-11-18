"""Implementation of Rule CV14."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler

# Window functions which ignore the window frame, and in some dialects reject
# an explicit one. Requiring a frame on these would be wrong.
_FRAMELESS_FUNCTIONS = frozenset(
    {
        "CUME_DIST",
        "DENSE_RANK",
        "LAG",
        "LEAD",
        "NTILE",
        "PERCENT_RANK",
        "RANK",
        "ROW_NUMBER",
    }
)


class Rule_CV14(BaseRule):
    """Window functions with an ``ORDER BY`` should specify a window frame.

    The frame used when a window definition has an ``ORDER BY`` but no frame
    clause is implicit, and depends on the dialect and on the function. For
    example, aggregate functions typically default to
    ``RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW``, while
    ``LAST_VALUE`` therefore returns the current row rather than the last row
    of the partition. This can lead to hard to spot bugs. Requiring the frame
    to be written out makes the author choose one deliberately.

    A window definition without an ``ORDER BY`` is not reported, because the
    frame is then the whole partition. Ranking and offset functions which do
    not use a frame (``ROW_NUMBER``, ``RANK``, ``DENSE_RANK``,
    ``PERCENT_RANK``, ``CUME_DIST``, ``NTILE``, ``LAG`` and ``LEAD``) are
    also not reported. A named window (``WINDOW w AS (...)``) is reported once,
    and only if a function which uses a frame refers to it. A window which
    only extends a named window without adding an ``ORDER BY``
    (``OVER (w)``) is checked where the named window is defined.

    This convention is opinionated, so this rule is **disabled by default**.
    It can be enabled with the ``force_enable = True`` flag:

    .. code-block:: cfg

        [sqlfluff:rules:convention.window_frame]
        force_enable = True

    **Anti-pattern**

    The window frame is implicit.

    .. code-block:: sql

        SELECT
            a,
            SUM(b) OVER (PARTITION BY a ORDER BY c) AS running_total
        FROM foo

    **Best practice**

    State the window frame explicitly.

    .. code-block:: sql

        SELECT
            a,
            SUM(b) OVER (
                PARTITION BY a
                ORDER BY c
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS running_total
        FROM foo
    """

    name = "convention.window_frame"
    aliases = ()
    groups: tuple[str, ...] = ("all", "convention")
    config_keywords = ["force_enable"]
    crawl_behaviour = SegmentSeekerCrawler({"window_specification"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Find window specifications with an ``ORDER BY`` and no frame."""
        # Config type hints
        self.force_enable: bool

        # This convention is opinionated, so the rule is disabled by default
        # and only runs when explicitly enabled via `force_enable = True`.
        if not self.force_enable:
            return None

        spec = context.segment
        if spec.get_child("frame_clause") or not spec.get_child("orderby_clause"):
            return None

        if not self._uses_frame(context):
            return None

        return LintResult(
            anchor=spec,
            description=(
                "Window definition has an ORDER BY but no explicit frame "
                "clause (ROWS, RANGE or GROUPS)."
            ),
        )

    @classmethod
    def _uses_frame(cls, context: RuleContext) -> bool:
        """Is the window used by anything which depends on its frame?"""
        parents = context.parent_stack
        # The specification is wrapped in brackets, which belong either to an
        # `OVER (...)` clause or to a named window expression.
        index = next(
            (
                i
                for i in range(len(parents) - 1, -1, -1)
                if parents[i].type != "bracketed"
            ),
            None,
        )
        if index is None:  # pragma: no cover
            return True
        owner = parents[index]

        if owner.is_type("over_clause"):
            function = parents[index - 1] if index > 0 else None
            return not cls._is_frameless_function(function)

        if owner.is_type("named_window_expression"):
            return cls._named_window_is_used_with_frame(owner, parents)

        return True  # pragma: no cover

    @staticmethod
    def _is_frameless_function(function: Optional[BaseSegment]) -> bool:
        """Is this a function which ignores the window frame?"""
        if function is None or not function.is_type("function"):
            return False
        function_name = function.get_child("function_name")
        if function_name is None:  # pragma: no cover
            return False
        # Ignore any schema qualification, e.g. `pg_catalog.row_number`.
        return function_name.raw_upper.rsplit(".", 1)[-1] in _FRAMELESS_FUNCTIONS

    @classmethod
    def _named_window_is_used_with_frame(
        cls,
        expression: BaseSegment,
        parents: tuple[BaseSegment, ...],
    ) -> bool:
        """Does any frame sensitive function use this named window?"""
        name_segment = expression.get_child("naked_identifier", "quoted_identifier")
        select = next(
            (seg for seg in reversed(parents) if seg.is_type("select_statement")),
            None,
        )
        if name_segment is None or select is None:  # pragma: no cover
            return True

        for function in select.recursive_crawl(
            "function", no_recursive_seg_type="select_statement"
        ):
            over_clause = function.get_child("over_clause")
            if over_clause is None:
                continue
            reference = over_clause.get_child("naked_identifier", "quoted_identifier")
            if (
                reference is not None
                and reference.raw_upper == name_segment.raw_upper
                and not cls._is_frameless_function(function)
            ):
                return True
        return False
