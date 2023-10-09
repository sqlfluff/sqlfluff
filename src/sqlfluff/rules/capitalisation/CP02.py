"""Implementation of Rule CP02."""

from typing import List, Optional

from sqlfluff.core.rules import LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.rules.capitalisation.CP01 import Rule_CP01
from sqlfluff.utils.identifers import identifiers_policy_applicable


class Rule_CP02(Rule_CP01):
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

    name = "capitalisation.identifiers"
    aliases = ("L014",)
    is_fix_compatible = True

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
            context.dialect.name in ["databricks", "sparksql"]
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
