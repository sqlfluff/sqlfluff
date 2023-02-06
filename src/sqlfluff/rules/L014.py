"""Implementation of Rule L014."""

from typing import Tuple, Optional, List

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.rules.L010 import Rule_L010


def identifiers_policy_applicable(
    policy: str, parent_stack: Tuple[BaseSegment, ...]
) -> bool:
    """Does `(un)quoted_identifiers_policy` apply to this segment?"""
    if policy == "all":
        return True
    if policy == "none":
        return False
    is_alias = parent_stack and parent_stack[-1].is_type(
        "alias_expression", "column_definition", "with_compound_statement"
    )
    if policy == "aliases" and is_alias:
        return True
    is_inside_from = any(p.is_type("from_clause") for p in parent_stack)
    if policy == "column_aliases" and is_alias and not is_inside_from:
        return True
    return False


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L014(Rule_L010):
    """Inconsistent capitalisation of unquoted identifiers.

    **Anti-pattern**

    In this example, unquoted identifier ``a`` is in lower-case but
    ``B`` is in upper-case.

    .. code-block:: sql

        select
            a,
            B
        from foo

    **Best practice**

    Ensure all unquoted identifiers are either in upper-case or in lower-case.

    .. code-block:: sql

        select
            a,
            b
        from foo

        -- Also good

        select
            A,
            B
        from foo

    """

    groups = ("all", "core")
    lint_phase = "post"
    crawl_behaviour = SegmentSeekerCrawler(
        {"naked_identifier", "properties_naked_identifier"}
    )
    config_keywords = [
        "extended_capitalisation_policy",
        "unquoted_identifiers_policy",
        "ignore_words",
        "ignore_words_regex",
    ]
    _description_elem = "Unquoted identifiers"

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        # Return None if identifier is case-sensitive property to enable Change
        # Data Feed
        # https://docs.delta.io/2.0.0/delta-change-data-feed.html#enable-change-data-feed
        if (
            context.dialect.name in ["sparksql"]
            and context.parent_stack
            and context.parent_stack[-1].type == "property_name_identifier"
            and context.segment.raw == "enableChangeDataFeed"
        ):
            return None

        if identifiers_policy_applicable(
            self.unquoted_identifiers_policy, context.parent_stack  # type: ignore
        ):
            return super()._eval(context=context)
        else:
            return [LintResult(memory=context.memory)]
