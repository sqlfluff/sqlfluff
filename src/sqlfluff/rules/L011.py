"""Implementation of Rule L011."""
from typing import List, Optional, Union

from sqlfluff.core.parser import (
    WhitespaceSegment,
    KeywordSegment,
)

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L011(BaseRule):
    """Implicit/explicit aliasing of table.

    Aliasing of table to follow preference
    (explicit using an `AS` clause is default).

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

    config_keywords = ["aliasing"]

    _target_elems = ("from_expression_element",)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Implicit aliasing of table/column not allowed. Use explicit `AS` clause.

        We look for the alias segment, and then evaluate its parent and whether
        it contains an AS keyword. This is the _eval function for both L011 and L012.

        The use of `raw_stack` is just for working out how much whitespace to add.

        """
        fixes = []

        if context.segment.is_type("alias_expression"):
            if context.parent_stack[-1].is_type(*self._target_elems):
                if any(e.name.lower() == "as" for e in context.segment.segments):
                    if self.aliasing == "implicit":  # type: ignore
                        if context.segment.segments[0].name.lower() == "as":

                            # Remove the AS as we're using implict aliasing
                            fixes.append(LintFix.delete(context.segment.segments[0]))
                            anchor = context.raw_stack[-1]

                            # Remove whitespace before (if exists) or after (if not)
                            if (
                                len(context.raw_stack) > 0
                                and context.raw_stack[-1].type == "whitespace"
                            ):
                                fixes.append(LintFix.delete(context.raw_stack[-1]))
                            elif (
                                len(context.segment.segments) > 0
                                and context.segment.segments[1].type == "whitespace"
                            ):
                                fixes.append(
                                    LintFix.delete(context.segment.segments[1])
                                )

                            return LintResult(anchor=anchor, fixes=fixes)

                else:
                    insert_buff: List[Union[WhitespaceSegment, KeywordSegment]] = []

                    # Add initial whitespace if we need to...
                    if context.raw_stack[-1].name not in ["whitespace", "newline"]:
                        insert_buff.append(WhitespaceSegment())

                    # Add an AS (Uppercase for now, but could be corrected later)
                    insert_buff.append(KeywordSegment("AS"))

                    # Add a trailing whitespace if we need to
                    if context.segment.segments[0].name not in [
                        "whitespace",
                        "newline",
                    ]:
                        insert_buff.append(WhitespaceSegment())

                    return LintResult(
                        anchor=context.segment,
                        fixes=[
                            LintFix.create_before(
                                context.segment.segments[0],
                                insert_buff,
                            )
                        ],
                    )
        return None
