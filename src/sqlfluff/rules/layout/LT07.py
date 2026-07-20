"""Implementation of Rule LT07."""

from typing import Optional, cast

from sqlfluff.core.parser import NewlineSegment, RawSegment
from sqlfluff.core.parser.segments import TemplateSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class Rule_LT07(BaseRule):
    """``WITH`` clause closing bracket should be on a new line.

    **Anti-pattern**

    In this example, the closing bracket is on the same line as CTE.

    .. code-block:: sql
       :force:

        WITH zoo AS (
            SELECT a FROM foo)

        SELECT * FROM zoo

    **Best practice**

    Move the closing bracket on a new line.

    .. code-block:: sql

        WITH zoo AS (
            SELECT a FROM foo
        )

        SELECT * FROM zoo

    """

    name = "layout.cte_bracket"
    aliases = ("L018",)
    groups = ("all", "core", "layout")
    crawl_behaviour = SegmentSeekerCrawler(
        {"with_compound_statement"}, provide_raw_stack=True
    )
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """WITH clause closing bracket should be aligned with WITH keyword.

        Look for a with clause and evaluate the position of closing brackets.
        """
        # We only trigger on start_bracket (open parenthesis)
        assert context.segment.is_type("with_compound_statement")

        # Find the end brackets for the CTE *query* (i.e. ignore optional
        # list of CTE columns).
        cte_end_brackets: set[RawSegment] = set()
        for cte in (
            FunctionalContext(context)
            .segment.children(sp.is_type("common_table_expression"))
            .iterate_segments()
        ):
            cte_bracketed = cte.children().last(sp.is_type("bracketed"))
            cte_start_bracket = cte_bracketed.children().first(
                sp.is_type("start_bracket")
            )
            cte_end_bracket = cte_bracketed.children().last(sp.is_type("end_bracket"))
            if cte_start_bracket and cte_end_bracket:
                self.logger.debug(
                    "Found CTE with brackets: %s & %s",
                    cte_start_bracket,
                    cte_end_bracket,
                )
                # Are they on the same line?
                # NOTE: We deliberately inspect the tree structure for a
                # newline between the brackets rather than comparing the
                # position markers (`line_no`) of the brackets. During an
                # in-progress fix pass another rule may have already inserted
                # newlines into the CTE body without the position markers
                # having been recomputed yet, so `line_no` can still report
                # the brackets as being on the same line. Relying on it left
                # `fix` non-idempotent: a CTE which *became* multi-line was
                # not picked up until a second pass. A structural newline
                # check reflects the current tree immediately.
                spans_multiple_lines = any(
                    elem.is_type("newline")
                    or (
                        elem.is_type("placeholder")
                        and cast(TemplateSegment, elem).source_str == "\n"
                    )
                    for elem in cte_bracketed[0].raw_segments
                )
                if not spans_multiple_lines:
                    # Same line
                    self.logger.debug("Skipping because on same line.")
                    continue
                # Otherwise add to the ones to check.
                cte_end_brackets.add(cast(RawSegment, cte_end_bracket[0]))

        for seg in cte_end_brackets:
            contains_non_whitespace = False
            idx = context.segment.raw_segments.index(seg)
            self.logger.debug("End bracket %s has idx %s", seg, idx)
            # Search backward through the raw segments from just before
            # the location of the bracket.
            for elem in context.segment.raw_segments[idx - 1 :: -1]:
                # If there's a literal newline, stop.
                if elem.is_type("newline"):
                    break
                # ...or a consumed newline in a placeholder.
                elif elem.is_type("placeholder"):
                    placeholder = cast(TemplateSegment, elem)
                    if placeholder.source_str == "\n":
                        break
                elif not elem.is_type("indent", "whitespace"):
                    self.logger.debug("Found non-whitespace: %s", elem)
                    contains_non_whitespace = True
                    break

            if contains_non_whitespace:
                # We have to move it to a newline
                return LintResult(
                    anchor=seg,
                    fixes=[
                        LintFix.create_before(
                            seg,
                            [
                                NewlineSegment(),
                            ],
                        )
                    ],
                )

        return None
