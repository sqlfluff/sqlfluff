"""Implementation of Rule CP05."""

from typing import List

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.base import LintResult
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.rules.capitalisation.CP01 import Rule_CP01


class Rule_CP05(Rule_CP01):
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

    name = "capitalisation.types"
    aliases = ("L063",)
    groups = ("all", "core", "capitalisation")
    is_fix_compatible = True

    crawl_behaviour = SegmentSeekerCrawler(
        {
            "data_type_identifier",
            "primitive_type",
            "datetime_type_identifier",
            "data_type",
        }
    )
    # NOTE: CP05 overrides `_eval` and then only calls
    # `_handle_segment` from CP01. Setting `_exclude_types`
    # and `_exclude_parent_types` therefore has no effect.
    # They are set here to empty tuples to avoid confusion.
    _exclude_types = ()
    _exclude_parent_types = ()
    config_keywords = [
        "extended_capitalisation_policy",
        "ignore_words",
        "ignore_words_regex",
    ]
    _description_elem = "Datatypes"

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Inconsistent capitalisation of datatypes.

        We use the `memory` feature here to keep track of cases known to be
        inconsistent with what we've seen so far as well as the top choice
        for what the possible case is.

        """
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
                res = self._handle_segment(seg, context)
                if res:
                    results.append(res)

        # NOTE: Given the dialect structure we can assume the targets have a parent.
        parent: BaseSegment = context.parent_stack[-1]
        # Don't process it if it's likely to have been processed by the parent.
        if context.segment.is_type("data_type_identifier") and not parent.is_type(
            "primitive_type", "datetime_type_identifier", "data_type"
        ):
            results.append(
                self._handle_segment(context.segment, context)
            )  # pragma: no cover

        return results
