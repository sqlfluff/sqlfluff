"""Implementation of Rule ST01."""

from typing import Optional, Tuple

from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class Rule_ST01(BaseRule):
    """Do not specify ``else null`` in a case when statement (redundant).

    **Anti-pattern**

    .. code-block:: sql

        select
            case
                when name like '%cat%' then 'meow'
                when name like '%dog%' then 'woof'
                else null
            end
        from x

    **Best practice**

    Omit ``else null``

    .. code-block:: sql

        select
            case
                when name like '%cat%' then 'meow'
                when name like '%dog%' then 'woof'
            end
        from x
    """

    name = "structure.else_null"
    aliases = ("L035",)
    groups: Tuple[str, ...] = ("all", "structure")
    crawl_behaviour = SegmentSeekerCrawler({"case_expression"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Find rule violations and provide fixes.

        0. Look for a case expression
        1. Look for "ELSE"
        2. Mark "ELSE" for deletion (populate "fixes")
        3. Backtrack and mark all newlines/whitespaces for deletion
        4. Look for a raw "NULL" segment
        5.a. The raw "NULL" segment is found, we mark it for deletion and return
        5.b. We reach the end of case when without matching "NULL": the rule passes
        """
        assert context.segment.is_type("case_expression")
        children = FunctionalContext(context).segment.children()
        else_clause = children.first(sp.is_type("else_clause"))

        # Does the "ELSE" have a "NULL"? NOTE: Here, it's safe to look for
        # "NULL", as an expression would *contain* NULL but not be == NULL.
        if else_clause and else_clause.children(
            lambda child: child.raw_upper == "NULL"
        ):
            # Found ELSE with NULL. Delete the whole else clause as well as
            # indents/whitespaces/meta preceding the ELSE. :TRICKY: Note
            # the use of reversed() to make select() effectively search in
            # reverse.
            before_else = children.reversed().select(
                start_seg=else_clause[0],
                loop_while=sp.or_(sp.is_type("whitespace", "newline"), sp.is_meta()),
            )
            return LintResult(
                anchor=context.segment,
                fixes=[LintFix.delete(else_clause[0])]
                + [LintFix.delete(seg) for seg in before_else],
            )
        return None
