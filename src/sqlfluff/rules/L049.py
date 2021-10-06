"""Implementation of Rule L049."""


from sqlfluff.core.rules.base import BaseRule, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L049(BaseRule):
    """Comparisons with NULL should use "IS" or "IS NOT".

    | **Anti-pattern**
    | In this example, the <> is used to check for NULL values'.

    .. code-block:: sql

        SELECT
            a
        FROM foo
        WHERE a <> NULL


    | **Best practice**
    | Use "IS" or "IS NOT" to check for NULL values.

    .. code-block:: sql

        SELECT
            a
        FROM foo
        WHERE a IS NOT NULL
    """

    def _eval(self, segment, **kwargs):
        """Relational operators should not be used to check for NULL values."""
        # Iterate through children of this segment looking for equals or "not
        # equals".
        if len(segment.segments) <= 2:
            return LintResult()

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
                operator = sub_seg
            elif operator:
                # Skip anything which is whitespace or non-code.
                if sub_seg.is_whitespace or not sub_seg.is_code:
                    continue
                if sub_seg.name == "null_literal":
                    self.logger.debug(
                        "Found NULL literal following equals/not equals @%s: %r",
                        sub_seg.pos_marker,
                        sub_seg.raw,
                    )
                    return LintResult(anchor=operator)

                else:
                    operator = None
