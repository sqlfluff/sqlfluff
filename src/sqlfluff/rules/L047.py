"""Implementation of Rule L047."""

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)


@document_configuration
@document_fix_compatible
class Rule_L047(BaseRule):
    """Use consistent syntax to express "count number of rows".

    COUNT(*) and COUNT(1) are equivalent syntaxes in many SQL engines
    due to optimizers interpreting these instructions as
    "count number of rows in result".

    The ANSI-92_ spec mentions the COUNT(*) syntax specifically as
    having a special meaning:

        If COUNT(*) is specified, then
        the result is the cardinality of T.

    So by default, SQLFluff enforces the consistent use of COUNT(*).

    If the SQL engine you work with, or your team, prefers COUNT(1)
    over COUNT(*) you can configure this rule to consistently enforce COUNT(1).

    .. _ANSI-92: http://msdn.microsoft.com/en-us/library/ms175997.aspx

    | **Anti-pattern**

    .. code-block:: sql

        select
            count(1)
        from table_a

    | **Best practice**
    |   Use count(*) unless specified otherwise by config ``prefer_count_1``

    .. code-block:: sql

        select
            count(*)
        from table_a

    """

    config_keywords = ["prefer_count_1"]

    def _eval(self, segment, **kwargs):
        """Find rule violations and provide fixes."""
        if (
            segment.is_type("function")
            and segment.get_child("function_name").raw_upper == "COUNT"
        ):
            f_content = [
                seg
                for seg in segment.segments
                if not seg.is_meta
                and not seg.is_type(
                    "start_bracket",
                    "end_bracket",
                    "function_name",
                    "whitespace",
                    "newline",
                )
            ]
            if len(f_content) != 1:
                return None

            if self.prefer_count_1 and f_content[0].is_type("star"):
                return LintResult(
                    anchor=segment,
                    fixes=[
                        LintFix(
                            "edit",
                            f_content[0],
                            f_content[0].edit(f_content[0].raw.replace("*", "1")),
                        ),
                    ],
                )
            if not self.prefer_count_1 and f_content[0].is_type("expression"):
                expression_content = [
                    seg for seg in f_content[0].segments if not seg.is_meta
                ]
                if (
                    len(expression_content) == 1
                    and expression_content[0].is_type("literal")
                    and expression_content[0].raw == "1"
                ):
                    return LintResult(
                        anchor=segment,
                        fixes=[
                            LintFix(
                                "edit",
                                expression_content[0],
                                expression_content[0].edit(
                                    expression_content[0].raw.replace("1", "*")
                                ),
                            ),
                        ],
                    )
