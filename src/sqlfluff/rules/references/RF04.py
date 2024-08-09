"""Implementation of Rule RF04."""

from typing import List, Optional

import regex

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.identifers import identifiers_policy_applicable


class Rule_RF04(BaseRule):
    """Keywords should not be used as identifiers.

    Although `unreserved` keywords `can` be used as identifiers,
    and `reserved words` can be used as quoted identifiers,
    best practice is to avoid where possible, to avoid any
    misunderstandings as to what the alias represents.

    .. note::
       Note that `reserved` keywords cannot be used as unquoted identifiers
       and will cause parsing errors and so are not covered by this rule.

    **Anti-pattern**

    In this example, ``SUM`` (built-in function) is used as an alias.

    .. code-block:: sql

        SELECT
            sum.a
        FROM foo AS sum

    **Best practice**

    Avoid keywords as the name of an alias.

    .. code-block:: sql

        SELECT
            vee.a
        FROM foo AS vee

    """

    name = "references.keywords"
    aliases = ("L029",)
    groups = ("all", "references")
    crawl_behaviour = SegmentSeekerCrawler({"naked_identifier", "quoted_identifier"})
    config_keywords = [
        "unquoted_identifiers_policy",
        "quoted_identifiers_policy",
        "ignore_words",
        "ignore_words_regex",
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Keywords should not be used as identifiers."""
        # Config type hints
        self.ignore_words_regex: str

        # Skip 1 letter identifiers. These can be datepart keywords
        # (e.g. "d" for Snowflake) but most people expect to be able to use them.
        if len(context.segment.raw) == 1:
            return LintResult(memory=context.memory)

        # Get the ignore list configuration and cache it
        try:
            ignore_words_list = self.ignore_words_list
        except AttributeError:
            # First-time only, read the settings from configuration.
            # So we can cache them for next time for speed.
            ignore_words_list = self._init_ignore_string()

        # Skip if in ignore list
        if ignore_words_list and context.segment.raw.lower() in ignore_words_list:
            return LintResult(memory=context.memory)

        # Skip if matches ignore regex
        if self.ignore_words_regex and regex.search(
            self.ignore_words_regex, context.segment.raw
        ):
            return LintResult(memory=context.memory)

        if (
            (
                context.segment.is_type("naked_identifier")
                and identifiers_policy_applicable(
                    self.unquoted_identifiers_policy,  # type: ignore
                    context.parent_stack,
                )
                and (
                    context.segment.raw.upper()
                    in context.dialect.sets("unreserved_keywords")
                )
            )
        ) or (
            (
                context.segment.is_type("quoted_identifier")
                and identifiers_policy_applicable(
                    self.quoted_identifiers_policy, context.parent_stack  # type: ignore
                )
                and (
                    context.segment.raw.upper()[1:-1]
                    in context.dialect.sets("unreserved_keywords")
                    or context.segment.raw.upper()[1:-1]
                    in context.dialect.sets("reserved_keywords")
                )
            )
        ):
            return LintResult(anchor=context.segment)
        else:
            return None

    def _init_ignore_string(self) -> List[str]:
        """Called first time rule is evaluated to fetch & cache the ignore_words."""
        # Use str() in case bools are passed which might otherwise be read as bool
        ignore_words_config = str(getattr(self, "ignore_words"))
        if ignore_words_config and ignore_words_config != "None":
            self.ignore_words_list = self.split_comma_separated_string(
                ignore_words_config.lower()
            )
        else:
            self.ignore_words_list = []

        ignore_words_list = self.ignore_words_list
        return ignore_words_list
