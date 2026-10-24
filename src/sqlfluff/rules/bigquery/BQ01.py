"""Implementation of Rule BQ01."""

from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.reflow.elements import ReflowPoint
from sqlfluff.utils.reflow.helpers import deduce_line_indent


class Rule_BQ01(BaseRule):
    """BigQuery chained function calls should follow the configured layout.

    With ``consistent`` (the default), use the first chain's first call boundary
    to infer the style for the file. Other styles are ``one_liner``, ``aligned``
    and ``indented``. This rule enforces call-boundary line breaks; LT02 handles
    indentation using the BigQuery grammar. Multiline arguments are preserved.
    Comments can prevent an automatic boundary fix.

    **Anti-pattern**

    With ``writing_style = aligned``, calls should start on separate lines.

    .. code-block:: sql

        SELECT (foo).LOWER().TRIM();

    **Best practice**

    With this rule and LT02 enabled:

    .. code-block:: sql

        SELECT (foo)
        .LOWER()
        .TRIM();
    """

    name = "bigquery.chained_functions"
    config_keywords = ["writing_style"]
    groups = ("all", "bigquery", "layout")
    crawl_behaviour = SegmentSeekerCrawler({"chained_function_call"})
    is_fix_compatible = True
    writing_style: str = "consistent"

    def _eval(self, context: RuleContext) -> list[LintResult]:
        """Enforce line breaks without calculating or correcting indentation."""
        if context.dialect.name != "bigquery":
            return []  # pragma: no cover

        gap = []
        for segment in reversed(context.siblings_pre):
            if segment.is_code:
                break
            gap.append(segment)
        gap.reverse()
        has_newline = any(segment.is_type("newline") for segment in gap)
        memory = context.memory or {}
        multiline = self.writing_style != "one_liner"
        if self.writing_style == "consistent":
            multiline = memory.setdefault("multiline", has_newline)

        whitespace = [seg for seg in gap if seg.is_type("whitespace", "newline")]
        if (multiline and has_newline) or (not multiline and not whitespace):
            return [LintResult(memory=memory)]

        # Crossing comments or template markers can change SQL semantics.
        safe_to_fix = all(
            seg.is_type("whitespace", "newline", "indent", "dedent") for seg in gap
        )
        description = (
            "Chained calls should start on a new line."
            if multiline
            else "Chained calls should touch the preceding expression."
        )
        if multiline and safe_to_fix:
            # Preserve the physical line's indent when inserting a boundary.
            # LT02 sets the required indentation from grammar markers.
            results, _ = ReflowPoint(
                segments=tuple(raw for seg in gap for raw in seg.raw_segments)
            ).indent_to(
                deduce_line_indent(
                    context.segment.raw_segments[0], context.parent_stack[0]
                ),
                before=context.segment.raw_segments[0],
                description=description,
            )
            for result in results:
                result.memory = memory
            return results

        return [
            LintResult(
                anchor=context.segment,
                description=description,
                fixes=[LintFix.delete(seg) for seg in whitespace]
                if safe_to_fix
                else [],
                memory=memory,
            )
        ]
