"""Implementation of Rule CV13."""

from typing import Optional

from sqlfluff.core.parser import SymbolSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CV13(BaseRule):
    """Avoid using ``+`` for string concatenation where not supported by dialect.

    Some dialects (e.g. Databricks, Spark, Postgres, BigQuery) do not support
    using the ``+`` operator for string concatenation. In those dialects the
    correct operator is ``||``. This rule flags cases where a ``+`` operator
    appears directly adjacent to a string literal and offers an automatic fix
    to replace it with ``||``.

    This rule is automatically disabled for dialects where ``+`` is a valid
    string concatenation operator (e.g. T-SQL).

    **Anti-pattern**

    Using ``+`` for string concatenation in a dialect that does not support it.

    .. code-block:: sql

        SELECT 'a' + 'b'

    **Best practice**

    Use ``||`` for string concatenation.

    .. code-block:: sql

        SELECT 'a' || 'b'

    """

    name = "convention.string_concatenation"
    aliases = ()
    groups = ("all", "convention")
    crawl_behaviour = SegmentSeekerCrawler({"expression"})
    is_fix_compatible = True

    # Dialects where || is the string concatenation operator.
    # In MySQL-family dialects, || is logical OR by default, so we skip those.
    _pipe_concat_dialects = frozenset({
        "ansi", "postgres", "bigquery", "snowflake", "databricks",
        "sparksql", "sqlite", "duckdb", "hive", "redshift", "oracle",
    })

    def _eval(self, context: RuleContext) -> Optional[list[LintResult]]:
        """Flag ``+`` used for string concatenation in unsupported dialects."""
        # Skip dialects where || is NOT the concat operator.
        if context.dialect.name not in self._pipe_concat_dialects:
            return None

        assert context.segment.is_type("expression")

        results: list[LintResult] = []
        segments = context.segment.segments

        for idx, seg in enumerate(segments):
            # We are looking for binary_operator segments with raw "+".
            if not (seg.is_type("binary_operator") and seg.raw == "+"):
                continue

            # Look at the non-whitespace/meta neighbours on either side.
            left = _find_non_whitespace(segments, idx, direction=-1)
            right = _find_non_whitespace(segments, idx, direction=1)

            if left is None or right is None:
                continue

            # Flag if at least one side is a string literal.
            if not (left.is_type("quoted_literal") or right.is_type("quoted_literal")):
                continue

            # Build fix: replace the "+" SymbolSegment with "||".
            concat_operator = SymbolSegment(raw="||", type="binary_operator")
            fix = LintFix.replace(seg, [concat_operator])

            results.append(
                LintResult(
                    anchor=seg,
                    fixes=[fix],
                    description=(
                        "Use '||' instead of '+' for string concatenation "
                        f"in {context.dialect.name}."
                    ),
                )
            )

        return results or None


def _find_non_whitespace(segments, idx, direction):
    """Walk segments from *idx* in *direction* skipping whitespace and meta."""
    if direction not in (-1, 1):
        raise ValueError("direction must be -1 or 1")
    i = idx + direction
    while 0 <= i < len(segments):
        seg = segments[i]
        if seg.is_type("whitespace", "newline", "indent", "dedent") or seg.is_meta:
            i += direction
            continue
        return seg
        i += direction
    return None
