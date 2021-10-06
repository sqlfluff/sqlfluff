"""Implementation of Rule L049."""


from sqlfluff.core.parser import KeywordSegment, WhitespaceSegment
from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L049(BaseRule):
    """Comparisons with NULL should use "IS" or "IS NOT".

    | **Anti-pattern**
    | In this example, the "=" operator is used to check for NULL values'.

    .. code-block:: sql

        SELECT
            a
        FROM foo
        WHERE a = NULL


    | **Best practice**
    | Use "IS" or "IS NOT" to check for NULL values.

    .. code-block:: sql

        SELECT
            a
        FROM foo
        WHERE a IS NULL
    """

    @staticmethod
    def _missing_whitespace(seg, before=True):
        """Check whether we're missing whitespace given an adjoining segment."""
        # There is a segment
        if not seg:
            return False
        # And it's not whitespace
        if seg.is_whitespace:
            return False
        # And it's not an opening/closing bracket
        if seg.name.endswith("_bracket"):
            if seg.name.startswith("start_" if before else "end_"):
                return False
        if seg.is_meta:  # pragma: no cover
            if before:
                if seg.source_str.endswith(" ") or seg.source_str.endswith("\n"):
                    return False
            else:
                if seg.source_str.startswith(" ") or seg.source_str.startswith("\n"):
                    return False
        return True

    @staticmethod
    def _find_segment(idx, segments, before=True):
        """Go back or forward to find the next relevant segment."""
        step = -1 if before else 1
        j = idx + step
        while (j >= 0) if before else (j < len(segments)):
            # Don't trigger on indents, but placeholders are allowed.
            if segments[j].is_type("indent"):
                j += step
            else:
                return segments[j]
        return None

    def _eval(self, segment, **kwargs):
        """Relational operators should not be used to check for NULL values."""
        # Context/motivation for this rule:
        # https://news.ycombinator.com/item?id=28772289
        # https://stackoverflow.com/questions/9581745/sql-is-null-and-null
        if len(segment.segments) <= 2:
            return LintResult()

        # Iterate through children of this segment looking for equals or "not
        # equals". Once found, check if the next code segment is a NULL literal.
        idx_operator = None
        operator = None
        for idx, sub_seg in enumerate(segment.segments):
            # Skip anything which is whitespace or non-code.
            if sub_seg.is_whitespace or not sub_seg.is_code:
                continue

            # Look for "=" or "<>".
            if not operator and sub_seg.name in ("equals", "not_equal_to"):
                self.logger.debug(
                    "Found equals/not equals @%s: %r", sub_seg.pos_marker, sub_seg.raw
                )
                idx_operator = idx
                operator = sub_seg
            elif operator:
                # Look for a "NULL" literal.
                if sub_seg.name == "null_literal":
                    self.logger.debug(
                        "Found NULL literal following equals/not equals @%s: %r",
                        sub_seg.pos_marker,
                        sub_seg.raw,
                    )
                    if sub_seg.raw[0] == "N":
                        is_seg = KeywordSegment("IS")
                        not_seg = KeywordSegment("NOT")
                    else:
                        is_seg = KeywordSegment("is")
                        not_seg = KeywordSegment("not")

                    edit = (
                        [is_seg]
                        if operator.name == "equals"
                        else [
                            is_seg,
                            WhitespaceSegment(),
                            not_seg,
                        ]
                    )
                    prev_seg = self._find_segment(
                        idx_operator, segment.segments, before=True
                    )
                    next_seg = self._find_segment(
                        idx_operator, segment.segments, before=False
                    )
                    if self._missing_whitespace(prev_seg, before=True):
                        edit = [WhitespaceSegment()] + edit
                    if self._missing_whitespace(next_seg, before=False):
                        edit = edit + [WhitespaceSegment()]
                    violation = LintResult(
                        anchor=operator,
                        fixes=[
                            LintFix(
                                "edit",
                                operator,
                                edit,
                            )
                        ],
                    )
                    return violation
