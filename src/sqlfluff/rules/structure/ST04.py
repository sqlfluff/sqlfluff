"""Implementation of Rule ST04."""

from sqlfluff.core.parser import BaseSegment, Indent, NewlineSegment, WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, Segments, sp
from sqlfluff.utils.reflow.reindent import construct_single_indent


class Rule_ST04(BaseRule):
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

    name = "structure.nested_case"
    aliases = ("L058",)
    groups = ("all", "structure")
    crawl_behaviour = SegmentSeekerCrawler({"case_expression"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> LintResult:
        """Nested CASE statement in ELSE clause could be flattened."""
        segment = FunctionalContext(context).segment
        assert segment.select(sp.is_type("case_expression"))
        case1_children = segment.children()
        case1_first_case = case1_children.first(sp.is_keyword("CASE")).get()
        assert case1_first_case
        case1_first_when = case1_children.first(
            sp.is_type("when_clause", "else_clause")
        ).get()
        case1_last_when = case1_children.last(sp.is_type("when_clause")).get()
        case1_else_clause = case1_children.select(sp.is_type("else_clause"))
        case1_else_expressions = case1_else_clause.children(sp.is_type("expression"))
        expression_children = case1_else_expressions.children()
        case2 = expression_children.select(sp.is_type("case_expression"))
        case2_children = case2.children()
        case2_first_case = case2_children.first(sp.is_keyword("CASE")).get()
        case2_first_when = case2_children.first(
            sp.is_type("when_clause", "else_clause")
        ).get()
        # The len() checks below are for safety, to ensure the CASE inside
        # the ELSE is not part of a larger expression. In that case, it's
        # not safe to simplify in this way -- we'd be deleting other code.
        if (
            not case1_last_when
            or len(case1_else_expressions) > 1
            or len(expression_children) > 1
            or not case2
        ):
            return LintResult()

        # Determine if we can combine the else case statement, the first and
        # second case expressions should be the same. If they aren't, that
        # case currently isn't handled.
        if [
            x.raw_upper
            for x in segment.children(sp.is_code())
            .select(start_seg=case1_first_case, stop_seg=case1_first_when)
            .raw_segments
        ] != [
            x.raw_upper
            for x in case2.children(sp.is_code())
            .select(start_seg=case2_first_case, stop_seg=case2_first_when)
            .raw_segments
        ]:
            return LintResult()

        # We can assert that this exists because of the previous check.
        assert case1_last_when
        # We can also assert that we'll also have an else clause because
        # otherwise the case2 check above would fail.
        case1_else_clause_seg = case1_else_clause.get()
        assert case1_else_clause_seg

        # Delete stuff between the last "WHEN" clause and the "ELSE" clause.
        case1_to_delete = case1_children.select(
            start_seg=case1_last_when, stop_seg=case1_else_clause_seg
        )
        # Restore any comments that were deleted
        after_last_comment_index = (
            case1_to_delete.find(case1_to_delete.last(sp.is_comment()).get()) + 1
        )
        case1_comments_to_restore = case1_to_delete.select(
            stop_seg=case1_to_delete.get(after_last_comment_index)
        )
        after_else_comment = case1_else_clause.children().select(
            select_if=sp.is_type("newline", "comment", "whitespace"),
            stop_seg=case1_else_expressions.get(),
        )

        # Delete the nested "CASE" expression.
        fixes = case1_to_delete.apply(LintFix.delete)

        tab_space_size: int = context.config.get("tab_space_size", ["indentation"])
        indent_unit: str = context.config.get("indent_unit", ["indentation"])

        # Determine the indentation to use when we move the nested "WHEN"
        # and "ELSE" clauses, based on the indentation of case1_last_when.
        # If no whitespace segments found, use default indent.
        when_indent_str = self._get_indentation(
            case1_children, case1_last_when, tab_space_size, indent_unit
        )
        # Again determine indentation, but matching the "CASE"/"END" level.
        end_indent_str = self._get_indentation(
            case1_children, case1_first_case, tab_space_size, indent_unit
        )

        # Move the nested "when" and "else" clauses after the last outer
        # "when".
        nested_clauses = case2.children(
            sp.is_type("when_clause", "else_clause", "newline", "comment", "whitespace")
        )

        # Rebuild the nested case statement.
        # Any comments after the last outer "WHEN" that were deleted
        segments = list(case1_comments_to_restore)
        # Any comments between the "ELSE" and nested "CASE"
        segments += self._rebuild_spacing(when_indent_str, after_else_comment)
        # The nested "WHEN", "ELSE" or "comments", with logical spacing
        segments += self._rebuild_spacing(when_indent_str, nested_clauses)
        fixes.append(LintFix.create_after(case1_last_when, segments, source=segments))

        # Delete the outer "else" clause.
        fixes.append(LintFix.delete(case1_else_clause_seg))
        # Add spacing for any comments that may exist after the nested `END`
        # but only on that same line.
        fixes += self._nested_end_trailing_comment(
            case1_children, case1_else_clause_seg, end_indent_str
        )
        return LintResult(case2[0], fixes=fixes)

    def _get_indentation(
        self,
        parent_segments: Segments,
        segment: BaseSegment,
        tab_space_size: int,
        indent_unit: str,
    ) -> str:
        """Calculate the indentation level for rebuilding nested struct.

        This is only a best attempt as the input may not be equally indented. The layout
        rules, if run, would resolve this.
        """
        leading_whitespace = (
            parent_segments.select(stop_seg=segment)
            .reversed()
            .first(sp.is_type("whitespace"))
        )
        seg_indent = parent_segments.select(stop_seg=segment).last(sp.is_type("indent"))
        indent_level = 1
        if (
            seg_indent
            and (segment_indent := seg_indent.get())
            and isinstance(segment_indent, Indent)
        ):
            indent_level = segment_indent.indent_val + 1
        indent_str = (
            "".join(seg.raw for seg in leading_whitespace)
            if leading_whitespace
            and (whitespace_seg := leading_whitespace.get())
            and len(whitespace_seg.raw) > 1
            else construct_single_indent(indent_unit, tab_space_size) * indent_level
        )

        return indent_str

    def _nested_end_trailing_comment(
        self,
        case1_children: Segments,
        case1_else_clause_seg: BaseSegment,
        end_indent_str: str,
    ) -> list[LintFix]:
        """Prepend newline spacing to comments on the final nested `END` line."""
        trailing_end = case1_children.select(
            start_seg=case1_else_clause_seg,
            loop_while=sp.not_(sp.is_type("newline")),
        )
        fixes = trailing_end.select(
            sp.is_whitespace(), loop_while=sp.not_(sp.is_comment())
        ).apply(LintFix.delete)
        first_comment = trailing_end.first(sp.is_comment()).get()
        if first_comment:
            segments = [NewlineSegment(), WhitespaceSegment(end_indent_str)]
            fixes.append(LintFix.create_before(first_comment, segments, segments))
        return fixes

    def _rebuild_spacing(
        self, indent_str: str, nested_clauses: Segments
    ) -> list[BaseSegment]:
        buff = []
        # If the first segment is a comment, add a newline
        prior_newline = nested_clauses.first(sp.not_(sp.is_whitespace())).any(
            sp.is_comment()
        )
        prior_whitespace = ""
        for seg in nested_clauses:
            if seg.is_type("when_clause", "else_clause") or (
                prior_newline and seg.is_comment
            ):
                buff += [NewlineSegment(), WhitespaceSegment(indent_str), seg]
                prior_newline = False
                prior_whitespace = ""
            elif seg.is_type("newline"):
                prior_newline = True
                prior_whitespace = ""
            elif not prior_newline and seg.is_comment:
                buff += [WhitespaceSegment(prior_whitespace), seg]
                prior_newline = False
                prior_whitespace = ""
            elif seg.is_whitespace:
                # Don't reset newline
                prior_whitespace = seg.raw
        return buff
