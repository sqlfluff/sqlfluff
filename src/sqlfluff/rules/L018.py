"""Implementation of Rule L018."""

from typing import cast

from sqlfluff.core.parser import (
    IdentitySet,
    NewlineSegment,
    PositionMarker,
)

from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.utils.functional import sp, FunctionalContext


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L018(BaseRule):
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

    groups = ("all", "core")
    crawl_behaviour = SegmentSeekerCrawler(
        {"with_compound_statement"}, provide_raw_stack=True
    )

    def _eval(self, context: RuleContext):
        """WITH clause closing bracket should be aligned with WITH keyword.

        Look for a with clause and evaluate the position of closing brackets.
        """
        # We only trigger on start_bracket (open parenthesis)
        assert context.segment.is_type("with_compound_statement")
        raw_stack_buff = list(context.raw_stack)
        # Look for the with keyword
        for seg in context.segment.segments:
            if seg.raw_upper == "WITH":
                seg_line_no = seg.pos_marker.line_no
                break
        else:  # pragma: no cover
            # This *could* happen if the with statement is unparsable,
            # in which case then the user will have to fix that first.
            if any(s.is_type("unparsable") for s in context.segment.segments):
                return LintResult()
            # If it's parsable but we still didn't find a with, then
            # we should raise that.
            raise RuntimeError("Didn't find WITH keyword!")

        # Find the end brackets for the CTE *query* (i.e. ignore optional
        # list of CTE columns).
        cte_end_brackets = IdentitySet()
        for cte in (
            FunctionalContext(context)
            .segment.children(sp.is_type("common_table_expression"))
            .iterate_segments()
        ):
            cte_end_bracket = (
                cte.children()
                .last(sp.is_type("bracketed"))
                .children()
                .last(sp.is_type("end_bracket"))
            )
            if cte_end_bracket:
                cte_end_brackets.add(cte_end_bracket[0])
        for seg in context.segment.iter_segments(
            expanding=["common_table_expression", "bracketed"], pass_through=True
        ):
            if seg not in cte_end_brackets:
                if not seg.is_type("start_bracket"):
                    raw_stack_buff.append(seg)
                continue

            if seg.pos_marker.line_no == seg_line_no:
                # Skip if it's the one-line version. That's ok
                continue

            # Is it all whitespace before the bracket on this line?
            assert seg.pos_marker

            contains_non_whitespace = False
            for elem in context.segment.raw_segments:
                if (
                    cast(PositionMarker, elem.pos_marker).line_no
                    == seg.pos_marker.line_no
                    and cast(PositionMarker, elem.pos_marker).line_pos
                    <= seg.pos_marker.line_pos
                ):
                    if elem is seg:
                        break
                    elif elem.is_type("newline"):
                        contains_non_whitespace = False
                    elif not elem.is_type("dedent") and not elem.is_type("whitespace"):
                        contains_non_whitespace = True

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
