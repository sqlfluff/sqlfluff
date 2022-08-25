"""Implementation of Rule L001."""
from sqlfluff.core.rules import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_groups,
)
from sqlfluff.utils.functional import FunctionalContext, sp


@document_groups
@document_fix_compatible
class Rule_L001(BaseRule):
    """Unnecessary trailing whitespace.

    **Anti-pattern**

    The ``•`` character represents a space.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo••

    **Best practice**

    Remove trailing spaces.

    .. code-block:: sql

        SELECT
            a
        FROM foo
    """

    groups = ("all", "core")
    crawl_behaviour = SegmentSeekerCrawler(
        {"newline", "end_of_file"}, provide_raw_stack=True
    )

    def _eval(self, context: RuleContext) -> LintResult:
        """Unnecessary trailing whitespace.

        Look for newline segments, and then evaluate what
        it was preceded by.
        """
        if len(context.raw_stack) > 0 and context.raw_stack[-1].is_type("whitespace"):
            # Look for a newline (or file end), which is preceded by whitespace
            deletions = (
                FunctionalContext(context)
                .raw_stack.reversed()
                .select(loop_while=sp.is_type("whitespace"))
            )
            # NOTE: The presence of a loop marker should prevent false
            # flagging of newlines before jinja loop tags.
            return LintResult(
                anchor=deletions[-1],
                fixes=[LintFix.delete(d) for d in deletions],
            )
        return LintResult()
