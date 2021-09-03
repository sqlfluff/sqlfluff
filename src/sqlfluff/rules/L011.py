"""Implementation of Rule L011."""

from sqlfluff.core.parser import WhitespaceSegment, KeywordSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L011(BaseRule):
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

    _target_elems = ("from_expression_element",)

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

                    # Add initial whitespace if we need to...
                    if raw_stack[-1].name not in ["whitespace", "newline"]:
                        insert_buff.append(WhitespaceSegment())

                    # Add an AS (Uppercase for now, but could be corrected later)
                    insert_buff.append(KeywordSegment("AS"))

                    # Add a trailing whitespace if we need to
                    if segment.segments[0].name not in ["whitespace", "newline"]:
                        insert_buff.append(WhitespaceSegment())

                    return LintResult(
                        anchor=segment,
                        fixes=[LintFix("create", segment.segments[0], insert_buff)],
                    )
        return None
