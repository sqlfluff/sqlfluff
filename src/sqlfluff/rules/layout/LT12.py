"""Implementation of Rule LT12."""

from typing import List, Optional, Tuple

from sqlfluff.core.parser import BaseSegment, NewlineSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.utils.functional import FunctionalContext, Segments, sp, tsp


def get_trailing_newlines(segment: BaseSegment) -> List[BaseSegment]:
    """Returns list of trailing newlines in the tree."""
    result = []
    for seg in segment.recursive_crawl_all(reverse=True):
        if seg.is_type("newline"):
            result.append(seg)
        if not seg.is_whitespace and not seg.is_type("dedent", "end_of_file"):
            break
    return result


def get_last_segment(segment: Segments) -> Tuple[List[BaseSegment], Segments]:
    """Returns rightmost & lowest descendant and its "parent stack"."""
    parent_stack: List[BaseSegment] = []
    while True:
        children = segment.children()
        if children:
            parent_stack.append(segment[0])
            segment = children.last(predicate=sp.not_(sp.is_type("end_of_file")))
        else:
            return parent_stack, segment


class Rule_LT12(BaseRule):
    """Files must end with a single trailing newline.

    **Anti-pattern**

    The content in file does not end with a single trailing newline. The ``$``
    represents end of file.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo$

        -- Ending on an indented line means there is no newline
        -- at the end of the file, the • represents space.

        SELECT
        ••••a
        FROM
        ••••foo
        ••••$

        -- Ending on a semi-colon means the last line is not a
        -- newline.

        SELECT
            a
        FROM foo
        ;$

        -- Ending with multiple newlines.

        SELECT
            a
        FROM foo

        $

    **Best practice**

    Add trailing newline to the end. The ``$`` character represents end of file.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo
        $

        -- Ensuring the last line is not indented so is just a
        -- newline.

        SELECT
        ••••a
        FROM
        ••••foo
        $

        -- Even when ending on a semi-colon, ensure there is a
        -- newline after.

        SELECT
            a
        FROM foo
        ;
        $

    """

    name = "layout.end_of_file"
    # Between 2.0.0 and 2.0.4 we supported had a kebab-case name for this rule
    # so the old name remains here as an alias to enable backward compatibility.
    aliases = ("L009", "layout.end-of-file")
    groups = ("all", "core", "layout")

    targets_templated = True
    # Use the RootOnlyCrawler to only call _eval() ONCE, with the root segment.
    crawl_behaviour = RootOnlyCrawler()
    lint_phase = "post"
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Files must end with a single trailing newline.

        We only care about the segment and the siblings which come after it
        for this rule, we discard the others into the kwargs argument.

        """
        # We only care about the final segment of the parse tree.
        parent_stack, segment = get_last_segment(FunctionalContext(context).segment)
        self.logger.debug("Found last segment as: %s", segment)
        if not segment:
            # NOTE: Edge case. If the file is totally empty, we won't find a final
            # segment. In this case return without error.
            return None

        trailing_newlines = Segments(*get_trailing_newlines(context.segment))
        trailing_literal_newlines = trailing_newlines
        self.logger.debug(
            "Untemplated trailing newlines: %s", trailing_literal_newlines
        )
        if context.templated_file:
            trailing_literal_newlines = trailing_newlines.select(
                loop_while=lambda seg: sp.templated_slices(
                    seg, context.templated_file
                ).all(tsp.is_slice_type("literal"))
            )
        self.logger.debug("Templated trailing newlines: %s", trailing_literal_newlines)
        if not trailing_literal_newlines:
            # We make an edit to create this segment after the child of the FileSegment.
            if len(parent_stack) == 1:
                fix_anchor_segment = segment[0]
            else:
                fix_anchor_segment = parent_stack[1]
            self.logger.debug("Anchor on: %s", fix_anchor_segment)

            return LintResult(
                anchor=segment[0],
                fixes=[
                    LintFix.create_after(
                        fix_anchor_segment,
                        [NewlineSegment()],
                    )
                ],
            )
        elif len(trailing_literal_newlines) > 1:
            # Delete extra newlines.
            return LintResult(
                anchor=segment[0],
                fixes=[LintFix.delete(d) for d in trailing_literal_newlines[1:]],
            )
        else:
            # Single newline, no need for fix.
            return None
