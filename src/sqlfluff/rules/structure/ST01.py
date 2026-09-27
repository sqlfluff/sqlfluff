"""Implementation of Rule ST01."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment, WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, Segments, sp


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
            # A comment between the ELSE and the NULL is a *child* of the
            # clause, so deleting the clause as one unit would delete the
            # user's comment with it. Keep any such comment by putting it
            # where the clause was, rather than deleting the clause outright.
            # c.f. ST04, which likewise restores comments when it removes an
            # else_clause from a case expression.
            comments = self._clause_comments(else_clause, before_else)
            if comments:
                return LintResult(
                    anchor=context.segment,
                    fixes=[LintFix.replace(else_clause[0], comments, source=comments)],
                )
            return LintResult(
                anchor=context.segment,
                fixes=[LintFix.delete(else_clause[0])]
                + [LintFix.delete(seg) for seg in before_else],
            )
        return None

    @classmethod
    def _clause_comments(
        cls, else_clause: Segments, before_else: Segments
    ) -> list[BaseSegment]:
        """Rebuild the clause's comments so they can stand in for the clause.

        Keeps every comment between the ELSE and the NULL and the line breaks
        between them, re-indenting any continuation line to the indent the
        ELSE had. Everything outside that span - the keyword, the NULL and
        the metas - is what the rule removes, so it is dropped.
        """
        clause_children = list(else_clause.children())
        comment_idxs = [
            idx for idx, seg in enumerate(clause_children) if seg.is_comment
        ]
        if not comment_idxs:
            return []

        indent = cls._else_indent(before_else)
        buff: list[BaseSegment] = []
        # The comments take the place of the ELSE, so the first one inherits
        # the clause's own indent and only later lines need re-indenting.
        after_newline = False
        for seg in clause_children[comment_idxs[0] : comment_idxs[-1] + 1]:
            if seg.is_type("newline"):
                buff.append(seg)
                after_newline = True
            elif seg.is_comment:
                if after_newline and indent:
                    buff.append(WhitespaceSegment(indent))
                buff.append(seg)
                after_newline = False
            elif seg.is_type("whitespace") and not after_newline:
                # Spacing between two comments on one line.
                buff.append(seg)
        return buff

    @staticmethod
    def _else_indent(before_else: Segments) -> str:
        """The whitespace between the last newline and the ELSE, if any.

        ``before_else`` runs backwards from the clause, so the whitespace is
        gathered in reverse and the walk stops at the line break. An ELSE
        which doesn't start its line has no indent to inherit.
        """
        indent = ""
        for seg in before_else:
            if seg.is_type("whitespace"):
                indent = seg.raw + indent
            elif seg.is_type("newline"):
                return indent
        return ""
