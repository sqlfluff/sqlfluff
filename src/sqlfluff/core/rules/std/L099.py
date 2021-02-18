"""Implementation of Rule L099."""

from sqlfluff.core.rules.base import BaseCrawler, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L099(BaseCrawler):
    """Query produces an unknown number of result columns.

    | **Anti-pattern**
    | Querying all columns using `*` produces a query result where the number
    | or ordering of columns may vary due to schema changes in upstream data
    | sources. This should be avoided because it is prone to breakage in
    | production.

    .. code-block::

        WITH cte AS (
            SELECT * FROM foo
        )

        SELECT * FROM cte

    | **Best practice**
    | Somewhere along the "path" to the source data, specify columns explicitly.

    .. code-block::

        WITH cte AS (
            SELECT * FROM foo
        )

        SELECT a, b FROM cte

    """

    _works_on_unparsable = False

    # with_compound_statement
    #   common_table_expression
    #     select_statement
    #       select_clause
    #         select_target_element
    #   common_table_expression ...
    #   select_statement
    #     select_clause
    #       select_target_element

    def _eval(self, segment, raw_stack, **kwargs):
        """Outermost query should produce known number of columns.
        """
        return None
        if segment.is_type("with_compound_statement"):
            raw_stack_buff = list(raw_stack)
            # Look for the with keyword
            for seg in segment.segments:
                if seg.name.lower() == "with":
                    seg_line_no = seg.pos_marker.line_no
                    break
            else:
                # This *could* happen if the with statement is unparsable,
                # in which case then the user will have to fix that first.
                if any(s.is_type("unparsable") for s in segment.segments):
                    return LintResult()
                # If it's parsable but we still didn't find a with, then
                # we should raise that.
                raise RuntimeError("Didn't find WITH keyword!")

            def indent_size_up_to(segs):
                seg_buff = []
                # Get any segments running up to the WITH
                for elem in reversed(segs):
                    if elem.is_type("newline"):
                        break
                    elif elem.is_meta:
                        continue
                    else:
                        seg_buff.append(elem)
                # reverse the indent if we have one
                if seg_buff:
                    seg_buff = list(reversed(seg_buff))
                indent_str = "".join(seg.raw for seg in seg_buff).replace(
                    "\t", " " * self.tab_space_size
                )
                indent_size = len(indent_str)
                return indent_size, indent_str

            balance = 0
            with_indent, with_indent_str = indent_size_up_to(raw_stack_buff)
            for seg in segment.iter_segments(expanding=["common_table_expression"]):
                if seg.name == "start_bracket":
                    balance += 1
                elif seg.name == "end_bracket":
                    balance -= 1
                    if balance == 0:
                        closing_bracket_indent, _ = indent_size_up_to(raw_stack_buff)
                        indent_diff = closing_bracket_indent - with_indent
                        # Is indent of closing bracket not the same as
                        # indent of WITH keyword.
                        if seg.pos_marker.line_no == seg_line_no:
                            # Skip if it's the one-line version. That's ok
                            pass
                        elif indent_diff < 0:
                            return LintResult(
                                anchor=seg,
                                fixes=[
                                    LintFix(
                                        "create",
                                        seg,
                                        self.make_whitespace(
                                            " " * (-indent_diff), seg.pos_marker
                                        ),
                                    )
                                ],
                            )
                        elif indent_diff > 0:
                            # Is it all whitespace before the bracket on this line?
                            prev_segs_on_line = [
                                elem
                                for elem in segment.iter_segments(
                                    expanding=["common_table_expression"]
                                )
                                if elem.pos_marker.line_no == seg.pos_marker.line_no
                                and elem.pos_marker.line_pos < seg.pos_marker.line_pos
                            ]
                            if all(
                                elem.is_type("whitespace") for elem in prev_segs_on_line
                            ):
                                # We can move it back, it's all whitespace
                                fixes = [
                                    LintFix(
                                        "create",
                                        seg,
                                        [
                                            self.make_whitespace(
                                                with_indent_str,
                                                seg.pos_marker.advance_by("\n"),
                                            )
                                        ],
                                    )
                                ] + [
                                    LintFix("delete", elem)
                                    for elem in prev_segs_on_line
                                ]
                            else:
                                # We have to move it to a newline
                                fixes = [
                                    LintFix(
                                        "create",
                                        seg,
                                        [
                                            self.make_newline(
                                                pos_marker=seg.pos_marker
                                            ),
                                            self.make_whitespace(
                                                with_indent_str,
                                                seg.pos_marker.advance_by("\n"),
                                            ),
                                        ],
                                    )
                                ]
                            return LintResult(anchor=seg, fixes=fixes)
                else:
                    raw_stack_buff.append(seg)
        return LintResult()
