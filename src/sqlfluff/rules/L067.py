"""Implementation of Rule L067."""

from sqlfluff.core.parser import NewlineSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
import sqlfluff.core.rules.functional.segment_predicates as sp


@document_groups
@document_configuration
@document_fix_compatible
class Rule_L067(BaseRule):

    """A subquery inside parentheses should start on a new line.
        For brackets, if there are any subqueries inside, the subqueries
        should begin on the next line after the starting bracket, and the
        ending bracket should go on the next line after the subquery.

    **Anti-pattern**

    Parentheses on the line with a subquery.

    .. code-block:: sql
        :force:

        SELECT A.SOMETHING
        FROM (SELECT
                B,
                C
            FROM D GROUP BY 1) AS A



    **Best practice**

    Opening bracket and ending bracket take a new line out of the subquery.

    .. code-block:: sql
        :force:

        SELECT A.SOMETHING
        FROM (
            SELECT
                B,
                C
            FROM D GROUP BY 1
        ) AS A

    """
    groups = ("all",)

    def _eval(self, context: RuleContext):
        if context.segment.is_type('bracketed'):
            expressions = context.functional.segment.children()
            start_bracket = context.segment.start_bracket[0] # Tuple of length 1
            end_bracket = context.segment.end_bracket[0]

            # Check whether there is any subquery found inside the brackets
            select_targets = expressions.select(sp.is_type("select_statement"))
            if select_targets:
                results = []
                # check if the select statement only take a single line.
                # If so, the parentheses can keep at the same line with them.
                if (
                    len(select_targets) == 1
                    and select_targets[0].get_start_loc()[0]
                    == select_targets[0].get_end_loc()[0]
                    == start_bracket.pos_marker.line_no
                    == end_bracket.pos_marker.line_no
                ):
                    return None

                # Otherwise, check and insert newlines after opening bracket and
                # before ending bracket. This rule won't care the indentation of
                # the subquery. It supposes L003 will take care of indentaion for it

                # Opening bracket: check whether the opening is at the same line
                # with the first select statement. If so, insert a new line and
                # clear the white space between opening and the select statement
                if (
                    select_targets[0].pos_marker.working_line_no
                    == start_bracket.pos_marker.working_line_no
                ):
                    fixes = []
                    whitespace_after_start_bracket = expressions.select(
                        sp.is_type("whitespace"),
                        start_seg=start_bracket,
                        stop_seg=select_targets[0]
                    )
                    fixes.extend(
                        [
                            LintFix.delete(ws)
                            for ws in whitespace_after_start_bracket
                        ]
                    )
                    fixes.append(
                        LintFix.create_after(
                            start_bracket,
                            [NewlineSegment()],
                        )
                    )
                    results.append(
                        LintResult(
                            anchor=start_bracket,
                            description=(
                                (
                                    "Subquery inside a bracket should go a new line. No "
                                    f"newline between opening bracket {start_bracket.raw} "
                                    "and subquery."
                                )
                            ),
                            fixes=fixes
                        )
                    )

                # Ending bracket: check whether the ending is at the same line
                # with the last segment of the last select statement. If so, insert
                # a new line and clear white space between the last segment and
                # the ending bracket
                if (
                    select_targets[-1].segments[-1].pos_marker.working_line_no
                    == end_bracket.pos_marker.working_line_no
                ):
                    fixes = []
                    whitespace_before_end_bracket = expressions.select(
                        sp.is_type("whitespace"),
                        start_seg=select_targets[-1],
                        stop_seg=end_bracket
                    )
                    fixes.extend(
                        [
                            LintFix.delete(ws)
                            for ws in whitespace_before_end_bracket
                        ]
                    )
                    fixes.append(
                        LintFix.create_before(
                            end_bracket,
                            [NewlineSegment()],
                        )
                    )
                    results.append(
                        LintResult(
                            anchor=end_bracket,
                            description=(
                                (
                                    "The ending bracket after a subquery should go a new "
                                    "line. No newline between the subquery and ending "
                                    f"bracket {end_bracket.raw}."
                                )
                            ),
                            fixes=fixes
                        )
                    )
                if results:
                    return results
