"""Implementation of Rule TQ05."""

from typing import Optional

from sqlfluff.core.parser import (
    BaseSegment,
    Dedent,
    Indent,
    KeywordSegment,
    NewlineSegment,
    WhitespaceSegment,
)
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.reflow.reindent import construct_single_indent


class Rule_TQ05(BaseRule):
    """``IF``, ``ELSE`` and ``WHILE`` bodies should be wrapped in ``BEGIN``/``END``.

    Without ``BEGIN``/``END`` only the first statement after the condition
    belongs to the ``IF``, ``ELSE`` or ``WHILE``. Later statements always run,
    which is easy to miss when reading or editing the code.

    This rule only applies to the ``tsql`` dialect and is disabled by
    default. Enable it with the ``force_enable = True`` flag.

    **Anti-pattern**

    .. code-block:: sql
       :force:

        IF @flag = 1
            SELECT * FROM Table1;

        SELECT * FROM Table2;

    **Best practice**

    Wrap each body in ``BEGIN``/``END``.

    .. code-block:: sql
       :force:

        IF @flag = 1
        BEGIN
            SELECT * FROM Table1;
        END

        SELECT * FROM Table2;
    """

    name = "tsql.if_while_begin_end"
    aliases = ()
    groups = ("all", "tsql")
    config_keywords = ["force_enable"]
    crawl_behaviour = SegmentSeekerCrawler({"if_then_statement", "while_statement"})
    is_fix_compatible = True

    _block_types = ("begin_end_block", "try_catch")

    def _eval(self, context: RuleContext) -> Optional[list[LintResult]]:
        """``IF``, ``ELSE`` and ``WHILE`` bodies should use ``BEGIN``/``END``."""
        self.force_enable: bool

        if not self.force_enable:
            return None

        if context.dialect.name != "tsql":
            return None  # pragma: no cover

        children = context.segment.segments
        results = []
        for idx, child in enumerate(children):
            if not child.is_type("statement"):
                continue
            first_code = next((seg for seg in child.segments if seg.is_code), None)
            if first_code is None or first_code.is_type(*self._block_types):
                continue
            results.append(
                LintResult(
                    anchor=child,
                    description="Wrap the body of IF, ELSE and WHILE in a "
                    "BEGIN/END block.",
                    fixes=self._wrap_body(context, children, idx),
                )
            )
        return results or None

    def _wrap_body(
        self, context: RuleContext, children: tuple[BaseSegment, ...], idx: int
    ) -> list[LintFix]:
        """Build fixes that put the body statement inside ``BEGIN``/``END``.

        The statement keeps its own whitespace. ``BEGIN`` and ``END`` go at
        the indent of the line that holds the ``IF``, ``ELSE`` or ``WHILE``.
        This is a best attempt. The layout rules, if run, resolve the rest.
        """
        statement = children[idx]
        root = context.parent_stack[0] if context.parent_stack else context.segment

        # Take the terminator and any comment on the same line into the block.
        moved: list[BaseSegment] = []
        pending: list[BaseSegment] = []
        for later in children[idx + 1 :]:
            if later.is_type("whitespace") or later.is_meta:
                pending.append(later)
            elif later.is_type("statement_terminator", "comment"):
                moved += [seg for seg in pending if not seg.is_meta] + [later]
                pending = []
            else:
                break

        owner = next(
            seg
            for seg in reversed(children[:idx])
            if seg.is_code and not seg.is_type("statement_terminator")
        )
        owner_line_start = self._line_start(root, owner.raw_segments[0])
        owner_indent = owner_line_start.raw if owner_line_start.is_whitespace else ""
        owner_idx = children.index(owner)
        on_new_line = any(
            seg.is_type("newline") for seg in children[owner_idx + 1 : idx]
        )

        body = [statement, *moved]
        fixes: list[LintFix] = []
        if on_new_line:
            leading = children[idx - 1]
            inner_ws = leading.raw if leading.is_type("whitespace") else ""
            outer = [WhitespaceSegment(owner_indent)] if owner_indent else []
            block_segments: tuple[BaseSegment, ...] = (
                KeywordSegment("BEGIN"),
                Indent(),
                NewlineSegment(),
                *([WhitespaceSegment(inner_ws)] if inner_ws else []),
                *body,
                NewlineSegment(),
                *outer,
                Dedent(),
                KeywordSegment("END"),
            )
            if leading.is_type("whitespace"):
                fixes.append(
                    LintFix.replace(leading, outer)
                    if outer
                    else LintFix.delete(leading)
                )
        else:
            unit = construct_single_indent(
                context.config.get("indent_unit", ["indentation"]),
                context.config.get("tab_space_size", ["indentation"]),
            )
            block_segments = (
                KeywordSegment("BEGIN"),
                Indent(),
                NewlineSegment(),
                WhitespaceSegment(owner_indent + unit),
                *body,
                NewlineSegment(),
                *([WhitespaceSegment(owner_indent)] if owner_indent else []),
                Dedent(),
                KeywordSegment("END"),
            )

        block = context.dialect.get_segment("BeginEndSegment")(segments=block_segments)
        wrapped = context.dialect.get_segment("StatementSegment")(segments=(block,))
        fixes.append(LintFix.replace(statement, [wrapped]))
        fixes += [LintFix.delete(seg) for seg in moved]
        return fixes

    @staticmethod
    def _line_start(root: BaseSegment, target: BaseSegment) -> BaseSegment:
        """Return the first raw segment on the line that holds ``target``."""
        raws = root.raw_segments
        pos = next(i for i, seg in enumerate(raws) if seg is target)
        while pos > 0 and not raws[pos - 1].is_type("newline"):
            pos -= 1
        return raws[pos]
