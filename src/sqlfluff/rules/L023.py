"""Implementation of Rule L023."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups

from sqlfluff.utils.functional import FunctionalContext, sp
from sqlfluff.utils.reflow.sequence import ReflowSequence


@document_groups
@document_fix_compatible
class Rule_L023(BaseRule):
    """Single whitespace expected after ``AS`` in ``WITH`` clause.

    **Anti-pattern**

    .. code-block:: sql

        WITH plop AS(
            SELECT * FROM foo
        )

        SELECT a FROM plop


    **Best practice**

    Add a space after ``AS``, to avoid confusing it for a function.
    The ``•`` character represents a space.

    .. code-block:: sql
       :force:

        WITH plop AS•(
            SELECT * FROM foo
        )

        SELECT a FROM plop
    """

    groups = ("all", "core")
    crawl_behaviour = SegmentSeekerCrawler({"common_table_expression"})
    target_keyword = "AS"
    strip_newlines = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Single whitespace expected in mother middle segment."""
        functional = FunctionalContext(context)

        as_keyword = (
            functional.segment.children(sp.is_keyword(self.target_keyword))
            .first()
            .get()
        )
        if not as_keyword:
            # No target keyword. Abort.
            return None

        # Respace the section immediately after the keyword. If any fixes
        # are returned it implies there was an issue.
        fixes = (
            ReflowSequence.from_around_target(
                as_keyword,
                context.parent_stack[0],
                config=context.config,
                sides="after",
            )
            .respace(strip_newlines=self.strip_newlines)
            .get_fixes()
        )
        if not fixes:
            # Spacing is good. Stop here.
            return None
        return LintResult(anchor=as_keyword, fixes=fixes)
