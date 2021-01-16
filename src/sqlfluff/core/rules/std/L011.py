"""Implementation of Rule L011."""

from sqlfluff.core.rules.base import BaseCrawler, LintResult, LintFix
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L011(BaseCrawler):
    """Implicit aliasing of table not allowed. Use explicit `AS` clause.

    | **Anti-pattern**
    | In this example, the alias 'voo' is implicit.

    .. code-block:: sql

        SELECT
            voo.a
        FROM foo voo

    | **Best practice**
    | Add `AS` to make it explicit.

    .. code-block:: sql

        SELECT
            voo.a
        FROM foo AS voo

    """

    _target_elems = ("table_expression",)

    def _eval(self, segment, parent_stack, raw_stack, **kwargs):
        """Implicit aliasing of table/column not allowed. Use explicit `AS` clause.

        We look for the alias segment, and then evaluate its parent and whether
        it contains an AS keyword. This is the _eval function for both L011 and L012.

        The use of `raw_stack` is just for working out how much whitespace to add.

        """
        if segment.is_type("alias_expression"):
            if parent_stack[-1].is_type(*self._target_elems):
                if not any(e.name.lower() == "as" for e in segment.segments):
                    insert_buff = []
                    insert_str = ""
                    init_pos = segment.segments[0].pos_marker

                    # Add initial whitespace if we need to...
                    if raw_stack[-1].name not in ["whitespace", "newline"]:
                        insert_buff.append(
                            self.make_whitespace(raw=" ", pos_marker=init_pos)
                        )
                        insert_str += " "

                    # Add an AS (Uppercase for now, but could be corrected later)
                    insert_buff.append(
                        self.make_keyword(
                            raw="AS", pos_marker=init_pos.advance_by(insert_str)
                        )
                    )
                    insert_str += "AS"

                    # Add a trailing whitespace if we need to
                    if segment.segments[0].name not in ["whitespace", "newline"]:
                        insert_buff.append(
                            self.make_whitespace(
                                raw=" ", pos_marker=init_pos.advance_by(insert_str)
                            )
                        )
                        insert_str += " "

                    return LintResult(
                        anchor=segment,
                        fixes=[LintFix("create", segment.segments[0], insert_buff)],
                    )
        return None
