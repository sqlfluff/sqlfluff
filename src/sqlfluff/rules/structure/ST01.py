"""Implementation of Rule ST01."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment, NewlineSegment, WhitespaceSegment
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
    groups: tuple[str, ...] = ("all", "structure")
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

            # Check for comment children in the else_clause that need to be
            # preserved. If found, re-home them after the last when_clause.
            comments = else_clause.children(sp.is_comment())
            fixes: list[LintFix] = []
            if comments:
                # Find the last when_clause to insert comments after it.
                last_when = children.last(sp.is_type("when_clause"))
                if last_when:
                    # Find the whitespace segment between last when and else.
                    # That whitespace contains the indentation for the else clause.
                    # NOTE: We loop through both newlines and whitespace to skip
                    # past any newlines before the indentation whitespace.
                    ws = children.select(
                        start_seg=last_when[0],
                        stop_seg=else_clause[0],
                        loop_while=sp.or_(sp.is_type("whitespace"), sp.is_type("newline")),
                    )
                    if ws:
                        # Determine the indentation to use for the re-homed comment.
                        # Use the last whitespace in the selection (the indentation
                        # that was before the else_clause).
                        ws_raw = ws[-1].raw
                        for comment in comments:
                            fixes.append(
                                LintFix.create_after(
                                    last_when[0],
                                    [NewlineSegment(), WhitespaceSegment(ws_raw), comment],
                                    source=[comment],
                                )
                            )
                    # If no whitespace found, fall through to normal deletion.

            # Delete the whole else clause as well as indents/whitespaces.
            fixes += [LintFix.delete(else_clause[0])]
            fixes += [LintFix.delete(seg) for seg in before_else]
            return LintResult(
                anchor=context.segment,
                fixes=fixes,
            )
        return None
