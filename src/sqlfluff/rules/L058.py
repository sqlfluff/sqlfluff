"""Implementation of Rule L058."""

from sqlfluff.core.parser import NewlineSegment, WhitespaceSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.core.rules.functional import sp


@document_fix_compatible
class Rule_L058(BaseRule):
    """Nested ``CASE`` statement in ``ELSE`` clause could be flattened.

    **Anti-pattern**

    In this example, the outer ``CASE``'s ``ELSE`` is an unnecessary, nested ``CASE``.

    .. code-block:: sql

        SELECT
          CASE
            WHEN species = 'Cat' THEN 'Meow'
            ELSE
            CASE
               WHEN species = 'Dog' THEN 'Woof'
            END
          END as sound
        FROM mytable

    **Best practice**

    Move the body of the inner ``CASE`` to the end of the outer one.

    .. code-block:: sql

        SELECT
          CASE
            WHEN species = 'Cat' THEN 'Meow'
            WHEN species = 'Dog' THEN 'Woof'
          END AS sound
        FROM mytable

    """

    def _eval(self, context: RuleContext) -> LintResult:
        """Nested CASE statement in ELSE clause could be flattened."""
        segment = context.functional.segment
        if segment.select(sp.is_type("case_expression")):
            case1_children = segment.children()
            case1_last_when = case1_children.last(sp.is_type("when_clause"))
            case1_else_clause = case1_children.select(sp.is_type("else_clause"))
            case2 = case1_else_clause.children(sp.is_type("expression")).children(
                sp.is_type("case_expression")
            )
            if not case1_last_when or not case2:
                return LintResult()

            # Delete stuff between the last "WHEN" clause and the "ELSE" clause.
            case1_to_delete = case1_children.select(
                start_seg=case1_last_when.get(), stop_seg=case1_else_clause.get()
            )

            # Delete the nested "CASE" expression.
            fixes = case1_to_delete.apply(lambda seg: LintFix.delete(seg))

            # Determine the indentation to use when we move the nested "WHEN"
            # and "ELSE" clauses, based on the indentation of case1_last_when.
            # If no whitespace segments found, use default indent.
            indent = (
                case1_children.select(stop_seg=case1_last_when.get())
                .reversed()
                .select(sp.is_type("whitespace"))
            )
            indent_str = "".join(seg.raw for seg in indent) if indent else self.indent

            # Move the nested "when" and "else" clauses after the last outer
            # "when".
            nested_clauses = case2.children(sp.is_type("when_clause", "else_clause"))
            create_after_last_when = nested_clauses.apply(
                lambda seg: [NewlineSegment(), WhitespaceSegment(indent_str), seg]
            )
            segments = [item for sublist in create_after_last_when for item in sublist]
            fixes.append(
                LintFix.create_after(case1_last_when.get(), segments, source=segments)
            )

            # Delete the outer "else" clause.
            fixes.append(LintFix.delete(case1_else_clause.get()))
            return LintResult(case2[0], fixes=fixes)
        return LintResult()
