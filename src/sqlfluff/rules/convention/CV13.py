"""Implementation of Rule CV13."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler

# Dialects where ``+`` is not a string concatenation operator and the engine
# rejects string operands outright rather than coercing them to numbers.
#
# This deliberately excludes the MySQL family (mysql, mariadb, doris,
# starrocks), which coerces string literals to numbers instead of raising, so
# ``'a' + 'b'`` is legal there and evaluates to 0. It also excludes tsql, where
# ``+`` *is* the concatenation operator.
_ERRORING_DIALECTS = ("sparksql", "databricks")


class Rule_CV13(BaseRule):
    """Do not use ``+`` to concatenate strings.

    In most dialects ``+`` is arithmetic only, and applying it to string
    operands is an error rather than concatenation. Spark and Databricks reject
    it with ``DATATYPE_MISMATCH.BINARY_OP_WRONG_TYPE``, but the query still
    parses, so the mistake is only found at runtime.

    Only the unambiguous case is flagged, where both operands are string
    literals. Deciding whether ``a + b`` concatenates or adds would require
    knowing the types of ``a`` and ``b``, which is out of scope for a parser.

    **Anti-pattern**

    Using ``+`` to join two string literals.

    .. code-block:: sql
       :force:

        SELECT 'a' + 'b' AS col
        FROM foo;

    **Best practice**

    Use the dialect's concatenation operator, ``||``, or the ``CONCAT``
    function.

    .. code-block:: sql
       :force:

        SELECT 'a' || 'b' AS col
        FROM foo;
    """

    name = "convention.string_concat"
    groups = ("all", "convention")
    crawl_behaviour = SegmentSeekerCrawler({"expression"})

    def _eval(self, context: RuleContext) -> Optional[list[LintResult]]:
        """Find ``+`` applied to two string literals."""
        assert context.segment.is_type("expression")

        if context.dialect.name not in _ERRORING_DIALECTS:
            return None

        # Whitespace, comments and meta segments are not code, so dropping them
        # leaves the operands and operators adjacent to each other.
        code = [seg for seg in context.segment.segments if seg.is_code]

        results = []
        for left, operator, right in zip(code, code[1:], code[2:]):
            if (
                operator.is_type("binary_operator")
                and operator.raw == "+"
                and left.is_type("quoted_literal")
                and right.is_type("quoted_literal")
            ):
                results.append(
                    LintResult(
                        anchor=operator,
                        description=(
                            "Strings should be concatenated with '||', not '+'."
                        ),
                    )
                )

        return results or None
