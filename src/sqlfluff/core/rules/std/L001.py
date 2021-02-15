"""Implementation of Rule L001."""
from sqlfluff.core.rules.base import BaseCrawler, LintResult, LintFix
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L001(BaseCrawler):
    """Unnecessary trailing whitespace.

    | **Anti-pattern**
    | The • character represents a space.

    .. code-block::

        SELECT
            a
        FROM foo••

    | **Best practice**
    | Remove trailing spaces.

    .. code-block::

        SELECT
            a
        FROM foo
    """

    def _eval(self, segment, raw_stack, **kwargs):
        """Unnecessary trailing whitespace.

        Look for newline segments, and then evaluate what
        it was preceded by.
        """
        # We only trigger on newlines
        if (
            segment.is_type("newline")
            and len(raw_stack) > 0
            and raw_stack[-1].is_type("whitespace")
        ):
            # If we find a newline, which is preceded by whitespace, then bad
            deletions = []
            idx = -1
            while raw_stack[idx].is_type("whitespace"):
                deletions.append(raw_stack[idx])
                idx -= 1
            return LintResult(
                anchor=deletions[-1], fixes=[LintFix("delete", d) for d in deletions]
            )
        return LintResult()
