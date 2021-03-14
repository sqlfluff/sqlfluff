"""Implementation of Rule L046."""

from sqlfluff.core.rules.base import BaseCrawler, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)


@document_configuration
@document_fix_compatible
class Rule_L046(BaseCrawler):
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
        if segment.is_type("function"):

            raw_upper_no_whitespaces = segment.raw_upper.replace(" ", "")

            if self.prefer_count_1 and raw_upper_no_whitespaces == "COUNT(*)":
                return LintResult(
                    anchor=segment,
                    fixes=[
                        LintFix(
                            "edit",
                            segment,
                            segment.get_child("star").edit(
                                segment.raw.replace("*", "1")
                            ),
                        ),
                    ],
                )

            if not self.prefer_count_1 and raw_upper_no_whitespaces == "COUNT(1)":
                return LintResult(
                    anchor=segment,
                    fixes=[
                        LintFix(
                            "edit",
                            segment,
                            segment.get_child("expression")
                            .get_child("literal")
                            .edit(segment.raw.replace("1", "*")),
                        ),
                    ],
                )
