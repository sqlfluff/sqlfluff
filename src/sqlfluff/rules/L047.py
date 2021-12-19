"""Implementation of Rule L047."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)


@document_configuration
@document_fix_compatible
class Rule_L047(BaseRule):
    """Use consistent syntax to express "count number of rows".

    Note:
        If both `prefer_count_1` and `prefer_count_0` are set to true
        then `prefer_count_1` has precedence.

    COUNT(*), COUNT(1), and even COUNT(0) are equivalent syntaxes in many SQL
    engines due to optimizers interpreting these instructions as
    "count number of rows in result".

    The ANSI-92_ spec mentions the COUNT(*) syntax specifically as
    having a special meaning:

        If COUNT(*) is specified, then
        the result is the cardinality of T.

    So by default, SQLFluff enforces the consistent use of COUNT(*).

    If the SQL engine you work with, or your team, prefers COUNT(1) or COUNT(0)
    over COUNT(*) you can configure this rule to consistently enforce your
    preference.

    .. _ANSI-92: http://msdn.microsoft.com/en-us/library/ms175997.aspx

    | **Anti-pattern**

    .. code-block:: sql

        select
            count(1)
        from table_a

    | **Best practice**
    | Use ``count(*)`` unless specified otherwise by config ``prefer_count_1``,
    | or ``prefer_count_0`` as preferred.

    .. code-block:: sql

        select
            count(*)
        from table_a

    """

    config_keywords = ["prefer_count_1", "prefer_count_0"]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Find rule violations and provide fixes."""
        # Config type hints
        self.prefer_count_0: bool
        self.prefer_count_1: bool

        if (
            context.segment.is_type("function")
            and context.segment.get_child("function_name").raw_upper == "COUNT"
        ):
            # Get bracketed content
            bracketed = context.segment.get_child("bracketed")

            if not bracketed:  # pragma: no cover
                return None

            f_content = [
                seg
                for seg in bracketed.segments
                if not seg.is_meta
                and not seg.is_type(
                    "start_bracket",
                    "end_bracket",
                    "whitespace",
                    "newline",
                )
            ]
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
                return LintResult(
                    anchor=context.segment,
                    fixes=[
                        LintFix.replace(
                            f_content[0],
                            [
                                f_content[0].edit(
                                    f_content[0].raw.replace("*", preferred)
                                )
                            ],
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
