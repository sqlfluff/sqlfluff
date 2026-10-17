"""Implementation of Rule LT16."""

from typing import Any

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.reflow.chained_layout import (
    DEFAULT_STYLE,
    RULE_NAME,
    infer_style,
    input_indent,
    preceding_gap,
    validate_style,
)
from sqlfluff.utils.reflow.elements import ReflowPoint
from sqlfluff.utils.reflow.reindent import construct_single_indent


class Rule_LT16(BaseRule):
    """Chained function calls should follow the configured layout.

    With ``consistent`` (the default), use the first chain's first call boundary
    to infer the style for the file. Other styles are ``one_liner``, ``aligned``
    and ``indented``. Only boundaries between calls are changed; multiline
    arguments remain multiline. Comments are preserved and may prevent a fix.

    **Anti-pattern**

    With ``writing_style = aligned``, calls should start on separate lines.

    .. code-block:: sql

        SELECT (foo).LOWER().TRIM();

    **Best practice**

    .. code-block:: sql

        SELECT
            (foo)
            .LOWER()
            .TRIM();
    """

    name = RULE_NAME
    config_keywords = ["writing_style"]
    groups = ("all", "layout")
    crawl_behaviour = SegmentSeekerCrawler({"chained_function_call"})
    is_fix_compatible = True
    writing_style: str = DEFAULT_STYLE

    def __init__(self, code: str, description: str, **kwargs: Any) -> None:
        super().__init__(code, description, **kwargs)
        self.writing_style = validate_style(self.writing_style)

    def _eval(self, context: RuleContext) -> list[LintResult]:
        """Select a style and propagate it between evaluations in this file."""
        gap = preceding_gap(context.siblings_pre)

        memory = context.memory or {}
        writing_style = self.writing_style
        if writing_style == "consistent":
            if "writing_style" not in memory:
                memory["writing_style"] = self._infer_style(context)
            writing_style = memory["writing_style"]

        result = self._lint_boundary(context, gap, writing_style)
        # Even a passing boundary must return the memory, otherwise a later
        # result can lose the file's selected style.
        if not result:
            return [LintResult(memory=memory)]
        results = result if isinstance(result, list) else [result]
        for item in results:
            item.memory = memory
        return results

    def _input_indent(self, context: RuleContext) -> str:
        """Find the initial input's line indentation, skipping previous calls."""
        return input_indent(context.siblings_pre, context.parent_stack[0])

    def _infer_style(self, context: RuleContext) -> str:
        """Infer the first chain's style from its first call boundary."""
        return infer_style(
            context.segment,
            context.siblings_pre,
            context.parent_stack[0],
            context.config.get("tab_space_size", ["indentation"]),
        )

    def _lint_boundary(
        self, context: RuleContext, gap: list[BaseSegment], writing_style: str
    ) -> LintResult | list[LintResult] | None:
        """Apply one concrete style without changing file-wide state."""
        # Only whitespace and structural indent markers are safe to cross.
        # In particular, deleting a newline after '--' would comment out code.
        safe_to_fix = all(
            seg.is_type("whitespace", "newline", "indent", "dedent") for seg in gap
        )
        if writing_style == "one_liner":
            whitespace = [seg for seg in gap if seg.is_type("whitespace", "newline")]
            if not whitespace:
                return None
            return LintResult(
                anchor=context.segment,
                description="Chained calls should touch the preceding expression.",
                fixes=[LintFix.delete(seg) for seg in whitespace]
                if safe_to_fix
                else [],
            )

        # Use the input's indentation, not a previous call's indentation.
        # Otherwise indented would add another level for every call.
        desired_indent = self._input_indent(context)
        if writing_style == "indented":
            desired_indent += construct_single_indent(
                context.config.get("indent_unit", ["indentation"]),
                context.config.get("tab_space_size", ["indentation"]),
            )

        description = f"Chained calls should use {writing_style} line breaks."
        if safe_to_fix:
            point = ReflowPoint(
                segments=tuple(raw for seg in gap for raw in seg.raw_segments)
            )
            results, _ = point.indent_to(
                desired_indent,
                before=context.segment.raw_segments[0],
                description=description,
            )
            return results

        # Comment-separated boundaries may already have the correct layout.
        # Check the suffix after their last newline without editing the comment.
        suffix = ""
        for segment in reversed(gap):
            if segment.is_type("newline"):
                if suffix == desired_indent:
                    return None
                break
            suffix = segment.raw + suffix
        return LintResult(
            anchor=context.segment,
            description=description,
        )
