"""Implementation of Rule L052."""
from typing import List, Optional

from sqlfluff.core.parser import SymbolSegment
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.raw import NewlineSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)


@document_configuration
@document_fix_compatible
class Rule_L052(BaseRule):
    """Statements must end with a semi-colon.

    | **Anti-pattern**
    | A statement is not immediately terminated with a semi-colon, the • represents space.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo

        ;

        SELECT
            b
        FROM bar••;

    | **Best practice**
    | Immediately terminate the statement with a semi-colon.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo;
    """

    config_keywords = ["semicolon_newline", "require_final_semicolon"]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Statements must end with a semi-colon."""
        # Config type hints
        self.semicolon_newline: bool
        self.require_final_semicolon: bool

        # First we can simply handle the case of existing semi-colon alignment.
        if context.segment.name == "semicolon":

            # Locate semicolon and iterate back over the raw stack
            # to find the end of the preceding statement.
            anchor_segment = context.segment
            pre_semicolon_segments = []
            for segment in context.raw_stack[::-1]:
                if segment.is_code:
                    break
                elif not segment.is_meta:
                    pre_semicolon_segments.append(segment)
                anchor_segment = segment

            # We can tidy up any whitespace between the semi-colon
            # and the preceding code/comment segment.
            whitespace_deletions = []
            for segment in pre_semicolon_segments:
                if not segment.is_whitespace:
                    break
                whitespace_deletions.append(segment)

            # Semi-colon on same line.
            if not self.semicolon_newline:

                if len(pre_semicolon_segments) >= 1:
                    # If preceding segments are found then delete the old
                    # semi-colon/preceding whitespace and then insert
                    # the semi-colon in the correct location.
                    fixes = [
                        LintFix(
                            "edit",
                            anchor_segment,
                            [
                                anchor_segment,
                                SymbolSegment(raw=";", type="symbol", name="semicolon"),
                            ],
                        ),
                        LintFix(
                            "delete",
                            context.segment,
                        ),
                    ]
                    fixes.extend(LintFix("delete", d) for d in whitespace_deletions)
                    return LintResult(
                        anchor=anchor_segment,
                        fixes=fixes,
                    )
            # Semi-colon on new line.
            else:
                if not (
                    (len(pre_semicolon_segments) == 1)
                    and all(s.is_type("newline") for s in pre_semicolon_segments)
                ):
                    # If preceding segment is not a single newline then delete the old
                    # semi-colon/preceding whitespace and then insert the
                    # semi-colon in the correct location.
                    fixes = [
                        LintFix(
                            "edit",
                            anchor_segment,
                            [
                                anchor_segment,
                                NewlineSegment(),
                                SymbolSegment(raw=";", type="symbol", name="semicolon"),
                            ],
                        ),
                        LintFix(
                            "delete",
                            context.segment,
                        ),
                    ]
                    fixes.extend(LintFix("delete", d) for d in whitespace_deletions)
                    return LintResult(
                        anchor=anchor_segment,
                        fixes=fixes,
                    )

        # SQL does not require a final trailing semi-colon, however
        # this rule looks to enforce that it is there.
        # Therefore we first locate the end of the file.
        if self.require_final_semicolon:
            # We only care about the final segment of the parse tree.
            if not self.is_final_segment(context):
                return None

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
                elif segment.is_code:
                    break
                anchor_segment = segment

            if not semi_colon_exist_flag:
                # Create the final semi-colon if it does not yet exist.
                if not self.semicolon_newline:
                    fixes = [
                        LintFix(
                            "edit",
                            anchor_segment,
                            [
                                anchor_segment,
                                SymbolSegment(raw=";", type="symbol", name="semicolon"),
                            ],
                        )
                    ]
                else:
                    fixes = [
                        LintFix(
                            "edit",
                            anchor_segment,
                            [
                                anchor_segment,
                                NewlineSegment(),
                                SymbolSegment(raw=";", type="symbol", name="semicolon"),
                            ],
                        )
                    ]

                return LintResult(
                    anchor=anchor_segment,
                    fixes=fixes,
                )

        return None
