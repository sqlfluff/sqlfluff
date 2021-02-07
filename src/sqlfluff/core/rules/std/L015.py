"""Implementation of Rule L015."""

from ..base import BaseCrawler, LintFix, LintResult


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
        # We only trigger on expressions that begin with start_bracket (open
        # parenthesis)
        if segment.type == "expression":
            segments_filt = self.filter_meta(segment.segments)
            if (
                len(segments_filt)
                and segments_filt[0].type == "start_bracket"
                and segments_filt[0].raw == "("
            ):
                filt_raw_stack = self.filter_meta(raw_stack)
                if len(filt_raw_stack) and filt_raw_stack[-1].name == "DISTINCT":
                    # If we find open_bracket immediately following DISTINCT,
                    # then bad.
                    fixes = []
                    if len(segments_filt) >= 2:
                        # Insert a single space after the open parenthesis being
                        # removed.
                        insert_str = " "
                        fixes.append(
                            LintFix(
                                "create",
                                self.filter_meta(segment.segments)[1],
                                [
                                    self.make_whitespace(
                                        raw=insert_str,
                                        pos_marker=segment.pos_marker.advance_by(
                                            insert_str
                                        ),
                                    )
                                ],
                            )
                        )
                    # Remove the parentheses.
                    fixes += [
                        LintFix("delete", segments_filt[0]),
                        LintFix("delete", segments_filt[-1]),
                    ]
                    return LintResult(anchor=segment, fixes=fixes)
        return None
