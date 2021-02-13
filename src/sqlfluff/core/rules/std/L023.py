"""Implementation of Rule L023."""

from typing import Optional, List

from sqlfluff.core.rules.base import BaseCrawler, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L023(BaseCrawler):
    """Single whitespace expected after AS in WITH clause.

    | **Anti-pattern**

    .. code-block::

        WITH plop AS(
            SELECT * FROM foo
        )

        SELECT a FROM plop


    | **Best practice**
    | The • character represents a space.
    | Add a space after AS, to avoid confusing
    | it for a function.

    .. code-block::

        WITH plop AS•(
            SELECT * FROM foo
        )

        SELECT a FROM plop
    """

    expected_mother_segment_type = "with_compound_statement"
    pre_segment_identifier = ("name", "AS")
    post_segment_identifier = ("type", "start_bracket")
    allow_newline = False
    expand_children: Optional[List[str]] = ["common_table_expression"]

    def _eval(self, segment, **kwargs):
        """Single whitespace expected in mother segment between pre and post segments."""
        error_buffer = []
        if segment.is_type(self.expected_mother_segment_type):
            last_code = None
            mid_segs = []
            for seg in segment.iter_segments(expanding=self.expand_children):
                if seg.is_code:
                    if (
                        last_code
                        and getattr(last_code, self.pre_segment_identifier[0])
                        == self.pre_segment_identifier[1]
                        and getattr(seg, self.post_segment_identifier[0])
                        == self.post_segment_identifier[1]
                    ):
                        # Do we actually have the right amount of whitespace?
                        raw_inner = "".join(s.raw for s in mid_segs)
                        if raw_inner != " " and not (
                            self.allow_newline
                            and any(s.name == "newline" for s in mid_segs)
                        ):
                            if not raw_inner:
                                # There's nothing between. Just add a whitespace
                                fixes = [
                                    LintFix(
                                        "create",
                                        seg,
                                        [
                                            self.make_whitespace(
                                                raw=" ", pos_marker=seg.pos_marker
                                            )
                                        ],
                                    )
                                ]
                            else:
                                # Don't otherwise suggest a fix for now.
                                # TODO: Enable more complex fixing here.
                                fixes = None
                            error_buffer.append(
                                LintResult(anchor=last_code, fixes=fixes)
                            )
                    mid_segs = []
                    if not seg.is_meta:
                        last_code = seg
                else:
                    mid_segs.append(seg)
        return error_buffer or None
