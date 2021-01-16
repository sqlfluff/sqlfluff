"""Implementation of Rule L035."""

from sqlfluff.core.rules.base import BaseCrawler, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L035(BaseCrawler):
    """Do not specify "else null" in a case when statement (redundant).

    | **Anti-pattern**

    .. code-block:: sql

        select
            case
                when name like '%cat%' then 'meow'
                when name like '%dog%' then 'woof'
                else null
            end
        from x

    | **Best practice**
    |  Omit "else null"

    .. code-block:: sql

        select
            case
                when name like '%cat%' then 'meow'
                when name like '%dog%' then 'woof'
            end
        from x
    """

    def _eval(self, segment, **kwargs):
        """Find rule violations and provide fixes.

        0. Look for a case expression
        1. Look for "ELSE"
        2. Mark "ELSE" for deletion (populate "fixes")
        3. Backtrack and mark all newlines/whitespaces for deletion
        4. Look for a raw "NULL" segment
        5.a. The raw "NULL" segment is found, we mark it for deletion and return
        5.b. We reach the end of case when without matching "NULL": the rule passes
        """
        if segment.is_type("case_expression"):
            fixes = []
            for idx, seg in enumerate(segment.segments):
                # When we find ELSE we delete
                # everything up to NULL
                if fixes:
                    fixes.append(LintFix("delete", seg))
                    # Safe to look for NULL, as an expression
                    # would contain NULL but not be == NULL
                    if seg.raw_upper == "NULL":
                        return LintResult(anchor=segment, fixes=fixes)

                if not fixes and seg.name == "ELSE":
                    fixes.append(LintFix("delete", seg))
                    # Walk back to remove indents/whitespaces
                    walk_idx = idx - 1
                    while (
                        segment.segments[walk_idx].name == "whitespace"
                        or segment.segments[walk_idx].name == "newline"
                        or segment.segments[walk_idx].is_meta
                    ):
                        fixes.append(LintFix("delete", segment.segments[walk_idx]))
                        walk_idx = walk_idx - 1
