"""Implementation of Rule L063."""

from typing import Tuple, List, Optional
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.base import LintResult
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler

from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.rules.L010 import Rule_L010


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L063(Rule_L010):
    """Inconsistent capitalisation of datatypes.

    **Anti-pattern**

    In this example, ``int`` and ``unsigned`` are in lower-case whereas
    ``VARCHAR`` is in upper-case.

    .. code-block:: sql

        CREATE TABLE t (
            a int unsigned,
            b VARCHAR(15)
        );

    **Best practice**

    Ensure all datatypes are consistently upper or lower case

    .. code-block:: sql

        CREATE TABLE t (
            a INT UNSIGNED,
            b VARCHAR(15)
        );

    """

    groups = ("all",)
    lint_phase = "post"
    crawl_behaviour = SegmentSeekerCrawler(
        {
            "data_type_identifier",
            "primitive_type",
            "datetime_type_identifier",
            "data_type",
        }
    )
    _target_elems: List[Tuple[str, str]] = [
        ("parenttype", "data_type"),
        ("parenttype", "datetime_type_identifier"),
        ("parenttype", "primitive_type"),
        ("type", "data_type_identifier"),
    ]
    _exclude_elements: List[Tuple[str, str]] = []
    config_keywords = [
        "extended_capitalisation_policy",
        "ignore_words",
        "ignore_words_regex",
    ]
    _description_elem = "Datatypes"

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Inconsistent capitalisation of keywords.

        We use the `memory` feature here to keep track of cases known to be
        INconsistent with what we've seen so far as well as the top choice
        for what the possible case is.

        """
        # Skip if not an element of the specified type/name
        parent: Optional[BaseSegment] = (
            context.parent_stack[-1] if context.parent_stack else None
        )
        if self.matches_target_tuples(context.segment, self._exclude_elements, parent):
            return [LintResult(memory=context.memory)]  # pragma: no cover

        results = []
        # For some of these segments we want to run the code on
        if context.segment.is_type(
            "primitive_type", "datetime_type_identifier", "data_type"
        ):
            for seg in context.segment.segments:
                # We don't want to edit symbols, quoted things or identifiers
                # if they appear.
                if seg.is_type(
                    "symbol", "identifier", "quoted_literal"
                ) or not seg.is_type("raw"):
                    continue
                res = self._handle_segment(seg, context.memory)
                if res:
                    results.append(res)

        # Don't process it if it's likely to have been processed by the parent.
        if context.segment.is_type("data_type_identifier") and not context.parent_stack[
            -1
        ].is_type("primitive_type", "datetime_type_identifier", "data_type"):
            results.append(
                self._handle_segment(context.segment, context.memory)
            )  # pragma: no cover

        return results
