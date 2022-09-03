"""Implementation of Rule L011."""
from typing import List, Optional, Tuple, Union

from sqlfluff.core.parser import (
    WhitespaceSegment,
    KeywordSegment,
)

from sqlfluff.core.rules import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L011(BaseRule):
    """Implicit/explicit aliasing of table.

    Aliasing of table to follow preference
    (requiring an explicit ``AS`` is the default).

    **Anti-pattern**

    In this example, the alias ``voo`` is implicit.

    .. code-block:: sql

        SELECT
            voo.a
        FROM foo voo

    **Best practice**

    Add ``AS`` to make it explicit.

    .. code-block:: sql

        SELECT
            voo.a
        FROM foo AS voo

    """

    groups: Tuple[str, ...] = ("all",)
    config_keywords = ["aliasing"]
    crawl_behaviour = SegmentSeekerCrawler({"alias_expression"}, provide_raw_stack=True)

    _target_elems: List[Tuple[str, str]] = [
        ("type", "from_expression_element"),
        ("type", "merge_statement"),
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Implicit aliasing of table/column not allowed. Use explicit `AS` clause.

        We look for the alias segment, and then evaluate its parent and whether
        it contains an AS keyword. This is the _eval function for both L011 and L012.
        """
        # Config type hints
        self.aliasing: str
        fixes = []
        raw_segment_pre = context.raw_stack[-1] if context.raw_stack else None

        assert context.segment.is_type("alias_expression")
        if self.matches_target_tuples(context.parent_stack[-1], self._target_elems):
            if any(e.raw_upper == "AS" for e in context.segment.segments):
                if self.aliasing == "implicit":
                    if context.segment.segments[0].raw_upper == "AS":

                        # Remove the AS as we're using implict aliasing
                        fixes.append(LintFix.delete(context.segment.segments[0]))
                        anchor = raw_segment_pre

                        # Remove whitespace before (if exists) or after (if not)
                        if (
                            raw_segment_pre is not None
                            and raw_segment_pre.type == "whitespace"
                        ):
                            fixes.append(LintFix.delete(raw_segment_pre))
                        elif (
                            len(context.segment.segments) > 0
                            and context.segment.segments[1].type == "whitespace"
                        ):
                            fixes.append(LintFix.delete(context.segment.segments[1]))

                        return LintResult(anchor=anchor, fixes=fixes)

            elif self.aliasing != "implicit":
                insert_buff: List[Union[WhitespaceSegment, KeywordSegment]] = []

                # Add initial whitespace if we need to...
                assert raw_segment_pre
                if not raw_segment_pre.is_type("whitespace", "newline"):
                    insert_buff.append(WhitespaceSegment())

                # Add an AS (Uppercase for now, but could be corrected later)
                insert_buff.append(KeywordSegment("AS"))

                # Add a trailing whitespace if we need to
                if not context.segment.segments[0].is_type(
                    "whitespace",
                    "newline",
                ):
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
