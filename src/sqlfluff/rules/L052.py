"""Implementation of Rule L052."""
from typing import List, Optional

from sqlfluff.core.parser import SymbolSegment
from sqlfluff.core.parser.segments.base import BaseSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L052(BaseRule):
    """Statements must end with a semi-colon.

    | **Anti-pattern**
    | A statement is not terminated with a semi-colon, the $ represents end of file.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo
        $

        -- Additionally space between the end of the statement
        -- and the semi-colon is forbidden, (the • represents space).

        SELECT
            a
        FROM foo••••;
        $

        -- Newlines between the end of the statement
        -- and the semi-colon are forbidden.

        SELECT
            a
        FROM foo
        ;

        -- These rules apply to all statements within multi-statement files.

        SELECT
            a
        FROM foo
        ;

        SELECT
            b
        FROM bar••;
        $

    | **Best practice**
    | Immediately terminate the statement with a semi-colon.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo;
        $

        -- For multi-statement files.

        SELECT
            a
        FROM foo;

        SELECT
            b
        FROM bar;
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Statements must end with a semi-colon."""
        # First we can simply handle the case of existing semi-colon alignment.
        whitespace_set = {"newline", "whitespace"}
        if context.segment.name == "semicolon":

            # Locate semicolon and iterate back over the raw stack to find
            # whitespace between the semi-colon and the end of the preceding statement.
            anchor_segment = context.segment
            whitespace_deletions = []
            for segment in context.raw_stack[::-1]:
                if segment.name not in whitespace_set:
                    break
                whitespace_deletions.append(segment)
                anchor_segment = segment

            # If whitespace is found then delete.
            if whitespace_deletions:
                return LintResult(
                    anchor=anchor_segment,
                    fixes=[LintFix("delete", d) for d in whitespace_deletions],
                )

        # SQL does not require a final trailing semi-colon, however
        # this rule looks to enforce that it is there.
        # Therefore we first locate the end of the file.
        if len(self.filter_meta(context.siblings_post)) > 0:
            # This can only fail on the last segment
            return None
        elif len(context.segment.segments) > 0:
            # This can only fail on the last base segment
            return None
        elif context.segment.is_meta:
            # We can't fail on a meta segment
            return None
        else:
            # So this looks like the end of the file, but we
            # need to check that each parent segment is also the last.
            # We do this with reference to the templated file, because it's
            # the best we can do given the information available.
            file_len = len(context.segment.pos_marker.templated_file.templated_str)
            pos = context.segment.pos_marker.templated_slice.stop
            # Does the length of the file equal the end of the templated position?
            if file_len != pos:
                return None

        # # Handle the edge case the end of the statement is the end of the file.
        # if

        # Include current segment for complete stack.
        complete_stack: List[BaseSegment] = list(context.raw_stack)
        complete_stack.append(context.segment)

        # Iterate backwards over complete stack to find
        # if the final semi-colon is already present.
        anchor_segment = context.segment
        semi_colon_exist_flag = False
        for segment in complete_stack[::-1]:  # type: ignore
            if segment.name == "semicolon":
                semi_colon_exist_flag = True
            elif (segment.name not in whitespace_set) and (not segment.is_meta):
                break
            anchor_segment = segment

        if not semi_colon_exist_flag:
            # Create the final semi-colon if it does not yet exist.
            return LintResult(
                anchor=anchor_segment,
                fixes=[
                    LintFix(
                        "edit",
                        anchor_segment,
                        [
                            anchor_segment,
                            SymbolSegment(raw=";", type="symbol", name="semicolon"),
                        ],
                    )
                ],
            )
        else:
            return None
