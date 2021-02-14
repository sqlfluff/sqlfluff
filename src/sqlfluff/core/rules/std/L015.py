"""Implementation of Rule L015."""

from sqlfluff.core.rules.base import BaseCrawler, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L015(BaseCrawler):
    """DISTINCT used with parentheses.

    | **Anti-pattern**
    | In this example, parenthesis are not needed and confuse
    | DISTINCT with a function. The parenthesis can also be misleading
    | in which columns they apply to.

    .. code-block:: sql

        SELECT DISTINCT(a), b FROM foo

    | **Best practice**
    | Remove parenthesis to be clear that the DISTINCT applies to
    | both columns.

    .. code-block:: sql

        SELECT DISTINCT a, b FROM foo

    """

    def _eval(self, segment, raw_stack, **kwargs):
        """Looking for DISTINCT before a bracket.

        Look for DISTINCT keyword immediately followed by open parenthesis.
        """
        # We only trigger when "DISTINCT" is the immediate parent of an
        # expression that begins with start_bracket.
        raw_stack_filtered = self.filter_meta(raw_stack)
        if raw_stack_filtered and raw_stack_filtered[-1].name == "DISTINCT":
            if segment.type == "expression":
                segments_filtered = self.filter_meta(segment.segments)
                if segments_filtered and segments_filtered[0].type == "start_bracket":
                    # If we find open_bracket immediately following DISTINCT,
                    # then bad.
                    fixes = []
                    # The end bracket could be anywhere in segments_filtered,
                    # e.g. if the expression is (a + b) * c. If and only if it's
                    # at the *end*, then the parentheses are unnecessary and
                    # confusing. Remove them.
                    if segments_filtered[-1].type == "end_bracket":
                        fixes += [
                            LintFix("delete", segments_filtered[0]),
                            LintFix("delete", segments_filtered[-1]),
                        ]
                        # Update segments_filtered to reflect the pending
                        # deletions.
                        segments_filtered = segments_filtered[1:-1]
                    # If there are still segments remaining after the potential
                    # deletions above, insert a space between DISTINCT and the
                    # remainder of the expression. (I think there will always
                    # be remaining segments; this is a sanity check to ensure
                    # we don't cause an IndexError.)
                    if segments_filtered:
                        # Insert a single space after the open parenthesis being
                        # removed. Reason: DISTINCT is not a function; it's more
                        # of a modifier that acts on all the columns. Therefore,
                        # adding a space makes it clearer what the SQL is
                        # actually doing.
                        insert_str = " "
                        first_segment = segments_filtered[0]
                        fixes.append(
                            LintFix(
                                "create",
                                first_segment,
                                [
                                    self.make_whitespace(
                                        raw=insert_str,
                                        pos_marker=first_segment.pos_marker.advance_by(
                                            insert_str
                                        ),
                                    )
                                ],
                            )
                        )
                    return LintResult(anchor=segment, fixes=fixes)
        return None
