"""Implementation of Rule CV04."""

from typing import Optional

from sqlfluff.core.parser import LiteralSegment, RawSegment, SymbolSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class Rule_CV04(BaseRule):
    """Use consistent syntax to express "count number of rows".

    Note:
        If both ``prefer_count_1`` and ``prefer_count_0`` are set to true
        then ``prefer_count_1`` has precedence.

    ``COUNT(*)``, ``COUNT(1)``, and even ``COUNT(0)`` are equivalent syntaxes
    in many SQL engines due to optimizers interpreting these instructions as
    "count number of rows in result".

    The ANSI-92_ spec mentions the ``COUNT(*)`` syntax specifically as
    having a special meaning:

        If COUNT(*) is specified, then
        the result is the cardinality of T.

    So by default, `SQLFluff` enforces the consistent use of ``COUNT(*)``.

    If the SQL engine you work with, or your team, prefers ``COUNT(1)`` or
    ``COUNT(0)`` over ``COUNT(*)``, you can configure this rule to consistently
    enforce your preference.

    .. _ANSI-92: http://msdn.microsoft.com/en-us/library/ms175997.aspx

    **Anti-pattern**

    .. code-block:: sql

        select
            count(1)
        from table_a

    **Best practice**

    Use ``count(*)`` unless specified otherwise by config ``prefer_count_1``,
    or ``prefer_count_0`` as preferred.

    .. code-block:: sql

        select
            count(*)
        from table_a

    """

    name = "convention.count_rows"
    aliases = ("L047",)
    groups = ("all", "core", "convention")
    config_keywords = ["prefer_count_1", "prefer_count_0"]
    crawl_behaviour = SegmentSeekerCrawler({"function"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Find rule violations and provide fixes."""
        # Config type hints
        self.prefer_count_0: bool
        self.prefer_count_1: bool
        new_segment: RawSegment

        # We already know we're in a function because of the crawl_behaviour.
        # This means it's very unlikely that there isn't a function_name here.
        function_name = context.segment.get_child("function_name")
        if not function_name:  # pragma: no cover
            return None

        if function_name.raw_upper == "COUNT":
            # Get bracketed content
            f_content = (
                FunctionalContext(context)
                .segment.children(sp.is_type("bracketed"))
                .children(
                    sp.and_(
                        sp.not_(sp.is_meta()),
                        sp.not_(
                            sp.is_type(
                                "start_bracket", "end_bracket", "whitespace", "newline"
                            )
                        ),
                    )
                )
            )
            if len(f_content) != 1:  # pragma: no cover
                return None

            preferred = "*"
            if self.prefer_count_1:
                preferred = "1"
            elif self.prefer_count_0:
                preferred = "0"

            if f_content[0].is_type("star") and (
                self.prefer_count_1 or self.prefer_count_0
            ):
                new_segment = LiteralSegment(raw=preferred, type="numeric_literal")
                return LintResult(
                    anchor=context.segment,
                    fixes=[
                        LintFix.replace(
                            f_content[0],
                            [new_segment],
                        ),
                    ],
                )

            if f_content[0].is_type("expression"):
                expression_content = [
                    seg for seg in f_content[0].segments if not seg.is_meta
                ]

                if (
                    len(expression_content) == 1
                    and expression_content[0].is_type("literal")
                    and expression_content[0].raw in ["0", "1"]
                    and expression_content[0].raw != preferred
                ):
                    if preferred == "*":
                        new_segment = SymbolSegment(raw=preferred, type="star")
                    else:
                        new_segment = LiteralSegment(
                            raw=preferred, type="numeric_literal"
                        )
                    return LintResult(
                        anchor=context.segment,
                        fixes=[
                            LintFix.replace(
                                expression_content[0],
                                [
                                    expression_content[0].edit(
                                        expression_content[0].raw.replace(
                                            expression_content[0].raw, preferred
                                        )
                                    ),
                                ],
                            ),
                        ],
                    )
        return None
